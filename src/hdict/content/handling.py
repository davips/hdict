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
from hosh import ø

from hdict import field
from hdict.content.abs.appliable import AbsAppliable
from hdict.content.abs.variable import AbsVariable
from hdict.indexeddict import IndexedDict


class Arg:
    def __init__(self, position: int):
        self.position = position

    def __hash__(self):
        return hash(self.position)

    def __lt__(self, other):
        return f"~{self.position}" < other

    def __repr__(self):
        return f"_{self.position}"


def check_dup(field_name, result):
    if field_name in result:  # pragma: no cover
        raise Exception(f"The same field cannot be provided more than once: {k}")


def handle_multioutput(result, field_names: tuple, content: list | dict | AbsAppliable | field):
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
    from hdict.content.subcontent import subcontent
    if isinstance(content, list):
        if len(field_names) != len(content):  # pragma: no cover
            raise Exception(f"Number of output fields ('{len(field_names)}') should match number of list elements ('{len(content)}').")
        for field_name, val in zip(field_names, content):
            if not isinstance(field_name, str):  # pragma: no cover
                raise Exception(f"Can only accept target-field strings when unpacking a list, not '{type(field_name)}'.")
            check_dup(field_name, result)
            result[field_name] = val
    elif isinstance(content, dict):
        if len(field_names) != len(content):  # pragma: no cover
            raise Exception(f"Number of output fields ('{len(field_names)}') should match number of dict entries ('{len(content)}').")
        for field_name, (_, val) in zip(field_names, sorted(content.items())):
            if not isinstance(field_name, str):  # pragma: no cover
                raise Exception(f"Can only accept target-field strings when unpacking a dict, not '{type(field_name)}'.")
            check_dup(field_name, result)
            result[field_name] = val
    elif isinstance(content, (AbsAppliable, field)):
        n = len(field_names)
        if all(isinstance(x, tuple) for x in field_names):
            source_target = sorted((sour, targ) for targ, sour in field_names)
            for i, sour_targ in enumerate(source_target):
                if len(sour_targ) != 2:  # pragma: no cover
                    raise Exception(f"Output tuples should be string pairs 'target=source', not a sequence of length '{len(sour_targ)}'.", sour_targ)
                source, target = sour_targ
                check_dup(target, result)
                result[target] = subcontent(content, i, n, source)
        elif any(isinstance(x, tuple) for x in field_names):  # pragma: no cover
            raise Exception(f"Cannot mix translated and non translated outputs.", field_names)
        else:
            for i, field_name in enumerate(field_names):
                check_dup(field_name, result)
                result[field_name] = subcontent(content, i, n)
    else:  # pragma: no cover
        raise Exception(f"Cannot handle multioutput for key '{field_names}' and type '{type(content)}'.")


def handle_args(signature, applied_args, applied_kwargs):
    from hdict import field
    from hdict.content.value import value
    from hdict import default

    # Separate positional from named parameters of 'f'.
    fargs, fkwargs = IndexedDict(), {}
    params = []
    hasargs, haskwargs = False, False
    if signature is None:
        # Applying a field.
        for v in applied_args:
            if not isinstance(v, field):  # pragma: no cover
                print(applied_args)
                raise Exception(f"Cannot apply a field ('{v}') with non field positional arguments.")  # TODO: why??
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
    wrap = lambda x: x if isinstance(x, AbsVariable) else value(x)
    used = set()
    for i, applied_arg in enumerate(applied_args):
        if i < len(fargs):
            # noinspection PyUnresolvedReferences
            used.add(key := fargs.keys()[i])
            fargs[key] = wrap(applied_arg)
        else:
            if i >= len(params):
                if not hasargs:  # pragma: no cover
                    raise Exception("Too many arguments to apply. No '*contentarg' detected for 'f'.")
                name = Arg(i)  # TODO: is this still useful?
            else:
                name = params[i]
                if name in fkwargs:
                    del fkwargs[name]
            fargs[name] = wrap(applied_arg)

    for applied_kwarg, v in applied_kwargs.items():
        if applied_kwarg in used:  # pragma: no cover
            raise Exception(f"Parameter '{applied_kwarg}' cannot appear in both 'contentarg' and 'kwargs' of 'apply()'.")
        if applied_kwarg in fargs:
            fargs[applied_kwarg] = wrap(v)
        elif applied_kwarg in fkwargs or haskwargs:
            fkwargs[applied_kwarg] = wrap(v)
        else:  # pragma: no cover
            raise Exception(f"Parameter '{applied_kwarg}' is not present in 'f' signature nor '**kwargs' was detected for 'f'.")

    return fargs, fkwargs


def handle_identity(data):
    hosh = ø
    ids = {}
    for k, v in data.items():
        # Handle meta. mirror, and field ids differently.
        if k.startswith("_"):  # pragma: no cover
            raise Exception("Custom metafields are not allowed:", k)
            # self.mhosh += self.data[k].hosh * k.encode()                # self.mids[k] = self.data[k].hosh.id
        elif k.endswith("_"):
            # mirrorfield, e.g.: 'df_' is a mirror/derived from 'df'
            pass
        else:
            try:
                hosh += data[k].hosh * k.encode()
            except AttributeError as e:  # pragma: no cover
                if "'sample' object has no attribute 'hosh'" in str(e):
                    raise Exception(f"Cannot apply before sampling.")
                raise e from None
            # PAPER REMINDER: state in the paper that hash(identifier) must be different from hash(value), for any identifier and value. E.g.: hash(X) != hash("X")    #   Here the difference always happen because values are pickled, while identifiers are just encoded().
            ids[k] = data[k].hosh.id
    return hosh, ids
