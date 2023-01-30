#  Copyright (c) 2023. Davi Pereira dos Santos
#  This file is part of the hdict project.
#  Please respect the license - more about this in the section (*) below.
#
#  hdict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  hdict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with hdict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#

from typing import Dict

from hdict import default
from hdict.entry.abs.abscontent import AbsContent
from hdict.hdict_ import hdict
from hdict.indexeddict import IndexedDict
from hdict.pandas import explode_df


class Unevaluated:
    pass


Unevaluated = Unevaluated()


class Arg:
    def __init__(self, position: int):
        self.position = position

    def __hash__(self):
        return hash(self.position)

    def __lt__(self, other):
        return f"~{self.position}" < other

    def __repr__(self):
        return f"_{self.position}"


def handle_multioutput(data, field_names: tuple, content: list | dict | AbsContent):
    """Fields and hoshes are assigned to each output according to the alphabetical order of the original keys.

    >>> from hdict import field
    >>> d = {"a": field("b"), "b": field("c"), "c": 5}
    >>> d
    {'a': field('b'), 'b': field('c'), 'c': 5}
    >>> handle_multioutput(d, ("x","y"), [0,1])
    >>> d
    {'a': field('b'), 'b': field('c'), 'c': 5, 'x': 0, 'y': 1}
    >>> handle_multioutput(d, ("x","y"), {1:"a", 0:"b"})
    >>> d
    {'a': field('b'), 'b': field('c'), 'c': 5, 'x': 'b', 'y': 'a'}
    """
    if isinstance(content, list):
        if len(field_names) != len(content):  # pragma: no cover
            raise Exception(f"Number of output fields ('{len(field_names)}') should match number of list elements ('{len(content)}').")
        for field_name, val in zip(field_names, content):
            if not isinstance(field_name, str):  # pragma: no cover
                raise Exception(f"Can only accept target-field strings when unpacking a list, not '{type(field_name)}'.")
            data[field_name] = val
    elif isinstance(content, dict):
        if len(field_names) != len(content):  # pragma: no cover
            raise Exception(f"Number of output fields ('{len(field_names)}') should match number of dict entries ('{len(content)}').")
        for field_name, (_, val) in zip(field_names, sorted(content.items())):
            if not isinstance(field_name, str):  # pragma: no cover
                raise Exception(f"Can only accept target-field strings when unpacking a dict, not '{type(field_name)}'.")
            data[field_name] = val
    elif isinstance(content, AbsContent):
        from hdict.subcontent import subcontent
        n = len(field_names)
        if all(isinstance(x, tuple) for x in field_names):
            source_target = sorted((sour, targ) for targ, sour in field_names)
            for i, sour_targ in enumerate(source_target):
                if len(sour_targ) != 2:  # pragma: no cover
                    raise Exception(f"Output tuples should be string pairs 'target=source', not a sequence of length '{len(sour_targ)}'.", sour_targ)
                source, target = sour_targ
                data[target] = subcontent(content, i, n, source)
        elif any(isinstance(x, tuple) for x in field_names):  # pragma: no cover
            raise Exception(f"Cannot mix translated and non translated outputs.", field_names)
        else:
            for i, field_name in enumerate(field_names):
                data[field_name] = subcontent(content, i, n)
    else:  # pragma: no cover
        raise Exception(f"Cannot handle multioutput for key '{field_names}' and type '{type(content)}'.", content)


def handle_args(signature, applied_args, applied_kwargs):
    from hdict import field
    from hdict.entry.value import value

    # Separate positional from named parameters of 'f'.
    fargs, fkwargs = IndexedDict(), {}
    params = []
    hasargs, haskwargs = False, False
    if signature is None:
        for v in applied_args:
            if not isinstance(v, field):  # pragma: no cover
                print(applied_args)
                raise Exception(f"Cannot apply a field ('{v}') with non field positional arguments.")
            fargs[v.name] = v
            params.append(v.name)
        for k, v in applied_kwargs.items():
            fkwargs[k] = v
            params.append(k)
    else:
        for par in signature.parameters.values():
            if str(par).startswith("**"):
                haskwargs = True
                continue
            elif str(par).startswith("*"):
                hasargs = True
                continue
            name = par.name
            if (v := par.default) is par.empty:
                fargs[name] = field(name)
            else:
                fkwargs[name] = default(v)
            params.append(name)

    # apply's entry override f's entry
    wrap = lambda x: x if isinstance(x, AbsContent) else value(x)
    used = set()
    for i, applied_arg in enumerate(applied_args):
        if i < len(fargs):
            # noinspection PyUnresolvedReferences
            used.add(key := fargs.keys()[i])
            fargs[key] = wrap(applied_arg)
        else:
            if i >= len(params):
                if not hasargs:  # pragma: no cover
                    raise Exception("Too many arguments to apply. No '*entry' detected for 'f'.")
                name = Arg(i)
            else:
                name = params[i]
                if name in fkwargs:
                    del fkwargs[name]
            fargs[name] = wrap(applied_arg)

    for applied_kwarg, v in applied_kwargs.items():
        if applied_kwarg in used:  # pragma: no cover
            raise Exception(f"Parameter '{applied_kwarg}' cannot appear in both 'entry' and 'kwargs' of 'apply()'.")
        if applied_kwarg in fargs:
            fargs[applied_kwarg] = wrap(v)
        elif applied_kwarg in fkwargs or haskwargs:
            fkwargs[applied_kwarg] = wrap(v)
        else:  # pragma: no cover
            raise Exception(f"Parameter '{applied_kwarg}' is not present in 'f' signature nor '**kwargs' was detected for 'f'.")

    return fargs, fkwargs


def handle_default(name, content, data):
    from hdict.entry.value import value
    from hdict.entry.field import field
    if name in data:
        while isinstance(data[name], field):
            name = data[name].name
        return field(name, content.hosh)
    return content.value if isinstance(content.value, field) else value(content.value, content.hosh)


def handle_values(data: Dict[str, object]):
    from hdict.entry.value import value
    from hdict.entry.apply import apply
    from hdict.entry.field import field
    from hdict.subcontent import subcontent
    unfinished = []
    for k, content in data.items():
        if isinstance(content, value):
            pass
        elif isinstance(content, default):  # pragma: no cover
            # data[k] = handle_default(k, content, data)
            raise Exception(f"Cannot pass object of type 'default' directly to hdict. Param:", k)
        # REMINDER: clone() makes a deep copy to avoid mutation in original 'content' when finishing it below
        elif isinstance(content, field):
            content = content.clone()
            unfinished.append(content)
            data[k] = content
        elif isinstance(content, (apply, subcontent)):
            content = content.clone()
            reqs = content.requirements
            for kreq, req in reqs.items():
                if isinstance(req, default):
                    reqs[kreq] = handle_default(kreq, req, data)
            unfinished.append(content)
            data[k] = content
        elif isinstance(content, hdict):
            data[k] = value(content.frozen, content.hosh)
        elif str(type(content)) == "<class 'pandas.core.frame.DataFrame'>":
            data[k] = explode_df(content)
        elif isinstance(content, AbsContent):  # pragma: no cover
            raise Exception(f"Cannot handle instance of type '{type(content)}'.")
        else:
            data[k] = value(content)

    # Finish state of field-dependent objects created above.
    for item in unfinished:
        if not item.finished:
            item.finish(data)
