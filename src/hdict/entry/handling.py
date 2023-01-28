from typing import Dict

from hdict import default
from hdict.entry.abscontent import AbsContent
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


def handle_args(signature, applied_args, applied_kwargs):
    from hdict import field
    from hdict.entry.value import value

    # Separate positional from named parameters of 'f'.
    fargs, fkwargs = IndexedDict(), {}
    hasargs, haskwargs = False, False
    params = []
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
            fkwargs[name] = default(name, v)
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
                if not hasargs:
                    raise Exception("Too many arguments to apply. No '*entry' detected for 'f'.")
                name = Arg(i)
            else:
                name = params[i]
                if name in fkwargs:
                    del fkwargs[name]
            fargs[name] = wrap(applied_arg)

    for applied_kwarg, v in applied_kwargs.items():
        if applied_kwarg in used:
            raise Exception(f"Parameter '{applied_kwarg}' cannot appear in both 'entry' and 'kwargs' of 'apply()'.")
        if applied_kwarg in fargs:
            fargs[applied_kwarg] = wrap(v)
        elif applied_kwarg in fkwargs or haskwargs:
            fkwargs[applied_kwarg] = wrap(v)
        else:
            raise Exception(f"Parameter '{applied_kwarg}' is not present in 'f' signature nor '**kwargs' was detected for 'f'.")

    return fargs, fkwargs


def handle_default(content, data):
    from hdict.entry.value import value
    from hdict.entry.field import field
    if content.name in data:
        return field(content.name, content.hosh)
    return content.value if isinstance(content.value, field) else value(content.value, content.hosh)


def handle_values(data: Dict[str, AbsContent | dict]):  # REMINDER: 'dict' entries are only "_id" and "_ids".
    from hdict.entry.value import value
    from hdict.entry.apply import apply
    from hdict.entry.field import field
    unfinished = []
    for k, content in data.items():
        if isinstance(content, value):
            pass
        elif isinstance(content, default):
            data[k] = handle_default(content, data)
        # REMINDER: clone() makes a deep copy to avoid mutation in original 'content' when finishing it below
        elif isinstance(content, field):
            content = content.clone()
            unfinished.append(content)
            data[k] = content
        elif isinstance(content, apply):
            content = content.clone()
            reqs = content.requirements
            for kreq, req in reqs.items():
                if isinstance(req, default):
                    reqs[kreq] = handle_default(req, data)
            unfinished.append(content)
            data[k] = content
        elif isinstance(content, hdict):
            data[k] = value(content.frozen, content.hosh)
        elif str(type(content)) == "<class 'pandas.core.frame.DataFrame'>":
            data[k] = explode_df(content)
        elif isinstance(content, AbsContent):
            raise Exception(f"Cannot handle instance of type '{type(content)}'.")
        else:
            data[k] = value(content)

    # Finish state of field-dependent objects created above.
    for item in unfinished:
        if not item.finished:
            item.finish(data)
