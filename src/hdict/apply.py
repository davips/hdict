from dataclasses import dataclass
from functools import cached_property
from inspect import signature, isfunction

from hdict.hoshfication import f2hosh
from hdict.indexeddict import IndexedDict
from hosh import Hosh


class Undefined:
    pass


Undefined = Undefined()


@dataclass
class val:
    obj: object

    def __hash__(self):
        return hash(self.obj)


@dataclass
class default:
    obj: object


class apply:  # TODO: allow_partial
    """
    >>> f = lambda a,b, c=1,d=2,e=13: 0
    >>> apply(f).args, apply(f).kwargs
    ({'a': 'a', 'b': 'b'}, {'c': default(obj=1), 'd': default(obj=2), 'e': default(obj=13)})
    >>> apply(f,3).input
    {'a': val(obj=3), 'b': 'b', 'c': default(obj=1), 'd': default(obj=2), 'e': default(obj=13)}
    >>> apply(f,3,4).input
    {'a': val(obj=3), 'b': val(obj=4), 'c': default(obj=1), 'd': default(obj=2), 'e': default(obj=13)}
    >>> apply(f,3,4,5).input
    {'a': val(obj=3), 'b': val(obj=4), 'c': val(obj=5), 'd': default(obj=2), 'e': default(obj=13)}
    >>> apply(f,3,4,5,6).input
    {'a': val(obj=3), 'b': val(obj=4), 'c': val(obj=5), 'd': val(obj=6), 'e': default(obj=13)}
    >>> apply(f,3,4,5,6,7).input
    {'a': val(obj=3), 'b': val(obj=4), 'c': val(obj=5), 'd': val(obj=6), 'e': val(obj=7)}
    >>> apply(f,d=5).input
    {'a': 'a', 'b': 'b', 'c': default(obj=1), 'd': val(obj=5), 'e': default(obj=13)}
    >>> f = lambda a,b, *args, c=1,d=2,e=13, **kwargs: 0
    >>> apply(f,3,4,5,6,7,8).input
    {'a': val(obj=3), 'b': val(obj=4), 'c': val(obj=5), 'd': val(obj=6), 'e': val(obj=7), 5: val(obj=8)}
    >>> apply(f,x=3,e=4,d=5,c=6,b=7,a=8).input
    {'a': val(obj=8), 'b': val(obj=7), 'c': val(obj=6), 'd': val(obj=5), 'e': val(obj=4), 'x': val(obj=3)}
    >>> apply(f,3,c=77,x=5).input
    {'a': val(obj=3), 'b': 'b', 'c': val(obj=77), 'd': default(obj=2), 'e': default(obj=13), 'x': val(obj=5)}
    >>> apply(f,b=77,x=5).input
    {'a': 'a', 'b': val(obj=77), 'c': default(obj=1), 'd': default(obj=2), 'e': default(obj=13), 'x': val(obj=5)}

    """

    def __init__(self, f: callable, *applied_args, allow_partial=False, hosh: Hosh = None, **applied_kwargs):
        self.f, self.allow_partial = f, allow_partial
        if isinstance(f, str):
            fargs = applied_args
            fkwargs = applied_kwargs
        #     TODO multifield
        else:
            if not isfunction(f):
                if not hasattr(f, "hosh"):
                    raise Exception(f"Missing 'hosh' attribute while applying custom callable class '{type(f)}'")
                sig = signature(self.f.__call__)
            else:
                self.hosh = (f2hosh(self.f) if hosh is None else hosh).rev
                sig = signature(self.f)
            wrap = lambda x: x if isinstance(x, (str, val)) else val(x)

            # Separate positional from named parameters of 'f'.
            fargs, fkwargs = IndexedDict(), {}
            hasargs, haskwargs = False, False
            params = []
            for par in sig.parameters.values():
                if str(par).startswith("**"):
                    haskwargs = True
                    continue
                elif str(par).startswith("*"):
                    hasargs = True
                    continue

                name = par.name
                if par.default is par.empty:
                    fargs[name] = name
                else:
                    fkwargs[name] = default(par.default)
                params.append(name)

            # apply's args override f's args
            used = set()
            for i, applied_arg in enumerate(applied_args):
                if i < len(fargs):
                    used.add(key := fargs.keys()[i])
                    fargs[key] = wrap(applied_arg)
                else:
                    if i >= len(params):
                        if not hasargs:
                            raise Exception("Too many arguments to apply. No '*args' detected for 'f'.")
                        name = i
                    else:
                        name = params[i]
                        if name in fkwargs:
                            del fkwargs[name]
                    fargs[name] = wrap(applied_arg)

            for applied_kwarg, v in applied_kwargs.items():
                if applied_kwarg in used:
                    raise Exception(f"Parameter '{applied_kwarg}' cannot appear in both 'args' and 'kwargs' of 'apply()'.")
                if applied_kwarg in fargs:
                    fargs[applied_kwarg] = wrap(v)
                elif applied_kwarg in fkwargs or haskwargs:
                    fkwargs[applied_kwarg] = wrap(v)
                else:
                    raise Exception(f"Parameter '{applied_kwarg}' is not present in 'f' signature nor '**kwargs' was detected for 'f'.")

        self.args = fargs
        self.kwargs = fkwargs

    @cached_property
    def input(self):
        return self.args | self.kwargs

    def deps__stub(self):
        return self.args.copy(), self.kwargs.copy()

    def multifield(k: tuple, v: [list, IndexedDict, "apply"]):
        pass
        # SubVal(self, item)
        # sorted(keys())
        # hosh[:n]
