from typing import Dict

from hdict.entry.absarg import AbsArg
from hdict.hdict_ import hdict
from hdict.indexeddict import IndexedDict
from hdict.pandas import explode_df


class Unevaluated:
    pass


Unevaluated = Unevaluated()


def handle_values(data: Dict[str, AbsArg | dict]):  # REMINDER: 'dict' entries are only "_id" and "_ids".
    from hdict import value, apply, field
    newdata, late_assignment = {}, []
    for k, v in data.items():
        if isinstance(v, value):
            newdata[k] = v
        elif isinstance(v, (apply, field)):
            late_assignment = v
            newdata[k] = v.clone()  # REMINDER: here we make a copy to avoid mutation in original 'v' while finishing it below
        elif isinstance(v, hdict):
            newdata[k] = value(v.frozen, v.hosh)
        elif str(type(v)) == "<class 'pandas.core.frame.DataFrame'>":
            newdata[k] = explode_df(v)
        elif isinstance(v, AbsArg):
            raise Exception(f"Cannot handle instance of type '{type(v)}'.")
        else:
            newdata[k] = value(v)

    # Finish state of field-dependent objects created above.
    for item in late_assignment:
        if isinstance(item, field):
            item.nest(newdata[item.name])
        if isinstance(item, apply):
            for k, dep in item.requirements.items():
                if isinstance(dep, field):
                    if dep.name not in newdata:
                        raise Exception(f"Missing field '{dep.name}'")
                    dep.nest(newdata[dep.name])
                elif isinstance(dep, value):
                    pass
                elif isinstance(dep, default):
                    if k in newdata:
                        dep.nest(newdata[k])
                else:
                    print(item.requirements.items(), k, dep)
                    raise Exception(f"Unknown type for dep_stub entry: '{type(dep)}")

    return newdata


def handle_args(signature, applied_args, applied_kwargs):
    from hdict import value, field
    from hdict.entry.default import default

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
        """
        def wrap(x, ispositional):
            match x:
                case val_(_, _):
                    return val_(x.obj, ispositional)
                case str():
                    return field(x, ispositional)
                case object():
                    return val_(x, ispositional)
        """
        if par.default is par.empty:
            fargs[name] = field(name, ispositional=True)
        else:
            fkwargs[name] = default.clone(par.default, ispositional=False) if isinstance(par.default,AbsArg) else default(par.default, ispositional=False)
        params.append(name)

    # apply's entry override f's entry
    used = set()
    for i, applied_arg in enumerate(applied_args):
        if i < len(fargs):
            used.add(key := fargs.keys()[i])
            fargs[key] = value(applied_arg, ispositional=True)
        else:
            if i >= len(params):
                if not hasargs:
                    raise Exception("Too many arguments to apply. No '*entry' detected for 'f'.")
                name = i
            else:
                name = params[i]
                if name in fkwargs:
                    del fkwargs[name]
            fargs[name] = value(applied_arg, ispositional=True)

    for applied_kwarg, v in applied_kwargs.items():
        if applied_kwarg in used:
            raise Exception(f"Parameter '{applied_kwarg}' cannot appear in both 'entry' and 'kwargs' of 'apply()'.")
        if applied_kwarg in fargs:
            fargs[applied_kwarg] = value(v, ispositional=True)
        elif applied_kwarg in fkwargs or haskwargs:
            fkwargs[applied_kwarg] = value(v, ispositional=False)
        else:
            raise Exception(f"Parameter '{applied_kwarg}' is not present in 'f' signature nor '**kwargs' was detected for 'f'.")

    return fargs, fkwargs
