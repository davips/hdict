from hdict.content.argument import AbsArgument
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


def handle_args(signature, applied_args, applied_kwargs):
    from hdict.content.argument.field import field
    from hdict.content.value import value

    # Separate positional from named parameters of 'f'.
    fargs, fkwargs = IndexedDict(), {}
    params = []
    hasargs, haskwargs = False, False
    if signature is None:
        # Applying a field.
        for i, v in enumerate(applied_args):
            fargs[i] = v
            params.append(i)
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
                from hdict.content.argument.default import default

                fkwargs[name] = default(v)
            params.append(name)

    # apply's entry override f's entry
    wrap = lambda x: x if isinstance(x, AbsArgument) else value(x)
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
                name = Arg(i)  # REMINDER: this is just a unique hash for the nameless argument
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
