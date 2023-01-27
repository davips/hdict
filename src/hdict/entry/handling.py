from dataclasses import dataclass
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
            # minor TODO: v cannot be an abscontent by now (default would need a recursive handling like 'field' and 'apply')
            #   would be mildly useful for functions that'd like to define a field as a default source as an alternative to the field given by the param name itself.
            fkwargs[name] = default(name, v)
        params.append(name)

    # apply's entry override f's entry
    wrap = lambda x: x if isinstance(x, AbsContent) else value(x)
    used = set()
    for i, applied_arg in enumerate(applied_args):
        if i < len(fargs):
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


def handle_values(data: Dict[str, AbsContent | dict]):  # REMINDER: 'dict' entries are only "_id" and "_ids".
    from hdict import apply, field
    from hdict.entry.value import value
    newdata, late_assignment = {}, []
    for k, v in data.items():
        if isinstance(v, value):
            newdata[k] = v
        elif isinstance(v, (apply, field)):
            new = v.clone()
            late_assignment.append(new)
            newdata[k] = new  # REMINDER: here we make a copy to avoid mutation in original 'v' while finishing it below
        elif isinstance(v, hdict):
            newdata[k] = value(v.frozen, v.hosh)
        elif str(type(v)) == "<class 'pandas.core.frame.DataFrame'>":
            newdata[k] = explode_df(v)
        elif isinstance(v, AbsContent):
            raise Exception(f"Cannot handle instance of type '{type(v)}'.")
        else:
            newdata[k] = value(v)

    # Finish state of field-dependent objects created above.
    for item in late_assignment:
        handle_item(item, newdata)

    return newdata


def handle_item(item: AbsContent, data):
    from hdict import apply, field, default
    from hdict.entry.value import value
    if isinstance(item, value):
        pass
    elif isinstance(item, field):
        if item.name not in data:
            raise Exception(f"Missing field '{item.name}'")
        if not item.iscloned:
            item = item.clone()
        item.fill(data[item.name])
    elif isinstance(item, default):
        item = data[item.name] if item.name in data else value(item, item.hosh)
    elif isinstance(item, apply):
        if not item.iscloned:
            item = item.clone()
        deps = item.requirements
        for k, dep in deps.items():
            if isinstance(dep, (field, apply, default)):
                newdep = handle_item(dep, data)
            else:
                print(k, dep, item.requirements.items())
                raise Exception(f"Unknown dep type '{type(dep)}'")
            deps[k] = newdep
        item.fill(deps)
    else:
        print(item)
        raise Exception(f"Unknown type for dep_stub entry: '{type(item)}")
    return item
