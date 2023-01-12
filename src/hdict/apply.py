from functools import cached_property
from inspect import signature, isfunction
from typing import Union

from hdict.hoshfication import f2hosh
from hdict.indexeddict import IndexedDict
from hdict.param import field, val, default
from hosh import Hosh


class Undefined:
    pass


Undefined = Undefined()



class apply:  # TODO: allow_partial
    """
    >>> f = lambda a,b, c=1,d=2,e=13: 0
    >>> apply(f).args, apply(f).kwargs
    ({'a': field(obj='a', ispositional=True), 'b': field(obj='b', ispositional=True)}, {'c': default(obj=1, ispositional=False), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False)})
    >>> apply(f,3).input
    {'a': val(obj=3, ispositional=True), 'b': field(obj='b', ispositional=True), 'c': default(obj=1, ispositional=False), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False)}
    >>> apply(f,3,4).input
    {'a': val(obj=3, ispositional=True), 'b': val(obj=4, ispositional=True), 'c': default(obj=1, ispositional=False), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False)}
    >>> apply(f,3,4,5).input
    {'a': val(obj=3, ispositional=True), 'b': val(obj=4, ispositional=True), 'c': val(obj=5, ispositional=True), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False)}
    >>> apply(f,3,4,5,6).input
    {'a': val(obj=3, ispositional=True), 'b': val(obj=4, ispositional=True), 'c': val(obj=5, ispositional=True), 'd': val(obj=6, ispositional=True), 'e': default(obj=13, ispositional=False)}
    >>> apply(f,3,4,5,6,7).input
    {'a': val(obj=3, ispositional=True), 'b': val(obj=4, ispositional=True), 'c': val(obj=5, ispositional=True), 'd': val(obj=6, ispositional=True), 'e': val(obj=7, ispositional=True)}
    >>> apply(f,d=5).input
    {'a': field(obj='a', ispositional=True), 'b': field(obj='b', ispositional=True), 'c': default(obj=1, ispositional=False), 'd': val(obj=5, ispositional=False), 'e': default(obj=13, ispositional=False)}
    >>> f = lambda a,b, *args, c=1,d=2,e=13, **kwargs: 0
    >>> apply(f,3,4,5,6,7,8).input
    {'a': val(obj=3, ispositional=True), 'b': val(obj=4, ispositional=True), 'c': val(obj=5, ispositional=True), 'd': val(obj=6, ispositional=True), 'e': val(obj=7, ispositional=True), 5: val(obj=8, ispositional=True)}
    >>> apply(f,x=3,e=4,d=5,c=6,b=7,a=8).input
    {'a': val(obj=8, ispositional=True), 'b': val(obj=7, ispositional=True), 'c': val(obj=6, ispositional=False), 'd': val(obj=5, ispositional=False), 'e': val(obj=4, ispositional=False), 'x': val(obj=3, ispositional=False)}
    >>> apply(f,3,c=77,x=5).input
    {'a': val(obj=3, ispositional=True), 'b': field(obj='b', ispositional=True), 'c': val(obj=77, ispositional=False), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False), 'x': val(obj=5, ispositional=False)}
    >>> apply(f,b=77,x=5).input
    {'a': field(obj='a', ispositional=True), 'b': val(obj=77, ispositional=True), 'c': default(obj=1, ispositional=False), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False), 'x': val(obj=5, ispositional=False)}

    """

    def __init__(self, f: Union[callable, str], *applied_args, allow_partial=False, hosh: Hosh = None, **applied_kwargs):
        self.f, self.allow_partial = f, allow_partial
        #     TODO multifield
        if isinstance(f, str):
            fargs = applied_args
            fkwargs = applied_kwargs
            fkwargs[f] = f
        else:
            if not isfunction(f):
                if not hasattr(f, "hosh"):
                    raise Exception(f"Missing 'hosh' attribute while applying custom callable class '{type(f)}'")
                sig = signature(self.f.__call__)
            else:
                self.hosh = (f2hosh(self.f) if hosh is None else hosh).rev
                sig = signature(self.f)

            def wrap(x, ispositional):
                match x:
                    case val(_, _):
                        return val(x.obj, ispositional)
                    case str():
                        return field(x, ispositional)
                    case object():
                        return val(x, ispositional)

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
                    fargs[name] = wrap(name, ispositional=True)
                else:
                    fkwargs[name] = default(par.default, ispositional=False)
                params.append(name)

            # apply's args override f's args
            used = set()
            for i, applied_arg in enumerate(applied_args):
                if i < len(fargs):
                    used.add(key := fargs.keys()[i])
                    fargs[key] = wrap(applied_arg, ispositional=True)
                else:
                    if i >= len(params):
                        if not hasargs:
                            raise Exception("Too many arguments to apply. No '*args' detected for 'f'.")
                        name = i
                    else:
                        name = params[i]
                        if name in fkwargs:
                            del fkwargs[name]
                    fargs[name] = wrap(applied_arg, ispositional=True)

            for applied_kwarg, v in applied_kwargs.items():
                if applied_kwarg in used:
                    raise Exception(f"Parameter '{applied_kwarg}' cannot appear in both 'args' and 'kwargs' of 'apply()'.")
                if applied_kwarg in fargs:
                    fargs[applied_kwarg] = wrap(v, ispositional=True)
                elif applied_kwarg in fkwargs or haskwargs:
                    fkwargs[applied_kwarg] = wrap(v, ispositional=False)
                else:
                    raise Exception(f"Parameter '{applied_kwarg}' is not present in 'f' signature nor '**kwargs' was detected for 'f'.")

        self.args = fargs
        self.kwargs = fkwargs

    @cached_property
    def input(self):
        return self.args | self.kwargs

    def deps__stub(self):
        return self.input.copy()

    def multifield(k: tuple, v: [list, IndexedDict, "apply"]):
        pass
        # SubVal(self, item)
        # sorted(keys())
        # hosh[:n]
