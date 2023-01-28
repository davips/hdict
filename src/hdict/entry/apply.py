from functools import reduce
from inspect import isfunction
from inspect import signature
from itertools import chain
from operator import mul
from typing import Union

from hdict.entry.abscontent import AbsContent
from hdict.entry.field import field
from hdict.entry.handling import Unevaluated, handle_args
from hdict.entry.value import value
from hdict.hoshfication import f2hosh
from hdict.indexeddict import IndexedDict
from hosh import Hosh
from hosh.misc import hoshes


class apply(AbsContent):
    """
    >>> from hdict import apply
    >>> f = lambda a, b: a**b
    >>> v = apply(f, 5, b=7)
    >>> v
    λ(a b)
    >>> g = lambda x, y: x**y
    >>> v.isevaluated
    False
    >>> apply(g, y=value(7), x=v)
    λ(x=λ(a b) y)

    >>> v2 = apply(f, a=v, b=value(7))
    >>> v2
    λ(a=λ(a b) b)
    >>> v.finish({})
    >>> v.value, v2
    (78125, λ(a b))
    >>> v2.finish({})
    >>> v2.value, v2
    (17763568394002504646778106689453125, 17763568394002504646778106689453125)

    >>> f = lambda a,b, c=1,d=2,e=13: 0
    >>> apply(f).requirements
    {'a': field('a'), 'b': field('b'), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> ap = apply(f,3)
    >>> ap.requirements
    {'a': 3, 'b': field('b'), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> ap
    λ(a b=field('b') c=default(1) d=default(2) e=default(13))
    >>> ap.finish({"b": value(77)})
    >>> ap
    λ(a b=b c=default(1) d=default(2) e=default(13))
    >>> from hdict.entry.handling import handle_values
    >>> d = {"f": ap, "b": 5, "d": 1, "e": field("b")}
    >>> d
    {'f': λ(a b=b c=default(1) d=default(2) e=default(13)), 'b': 5, 'd': 1, 'e': field('b')}
    >>> handle_values(d)
    >>> d
    {'f': λ(a b=b c d=d e=b), 'b': 5, 'd': 1, 'e': b}
    >>> apply(f,3,4).requirements
    {'a': 3, 'b': 4, 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5,6).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': default(13)}
    >>> apply(f,3,4,5,6,7).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7}
    >>> apply(f,d=5).requirements
    {'a': field('a'), 'b': field('b'), 'c': default(1), 'd': 5, 'e': default(13)}
    >>> f = lambda a,b, *entry, c=1,d=2,e=13, **kwargs: 0
    >>> apply(f,3,4,5,6,7,8).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7, _5: 8}
    >>> apply(f,x=3,e=4,d=5,c=6,b=7,a=8).requirements
    {'a': 8, 'b': 7, 'c': 6, 'd': 5, 'e': 4, 'x': 3}
    >>> apply(f,3,c=77,x=5).requirements
    {'a': 3, 'b': field('b'), 'c': 77, 'd': default(2), 'e': default(13), 'x': 5}
    >>> apply(f,b=77,x=5).requirements
    {'a': field('a'), 'b': 77, 'c': default(1), 'd': default(2), 'e': default(13), 'x': 5}
    """
    out = None
    _value = Unevaluated
    _hosh = None
    _finished = False

    #     TODO multifield
    def __init__(self, f: Union[callable, "apply", field], *applied_args, fhosh: Hosh = None, **applied_kwargs):
        self.f = f
        if isinstance(fhosh, str):
            fhosh = Hosh.fromid(fhosh)
        if isinstance(f, apply):  # "clone" mode
            fun = f.fun
            self.fhosh = f.fhosh
            self.args = f.args
            self.kwargs = f.kwargs
            from hdict.entry.default import default
            self.requirements = {k: req.clone() if isinstance(req, (field, apply, default)) else req for k, req in f.requirements.items()}
        elif isinstance(f, field):  # "function will be provided by hdict"-mode constrains 'applied_args'
            self.fhosh = fhosh
            fun = lambda *args, **kwargs: f.value(*args, **kwargs)
            self.args, self.kwargs = handle_args(None, applied_args, applied_kwargs)
            self.requirements = {k: v for k, v in sorted((self.args | self.kwargs).items())}
        elif callable(fun := f):
            if not isfunction(fun):  # "not function" means "custom callable"
                if not hasattr(fun, "__call__"):
                    raise Exception(f"Cannot infer method to apply non custom callable type '{type(fun)}'.")
                if not hasattr(fun, "hosh"):
                    raise Exception(f"Missing 'hosh' attribute while applying custom callable class '{type(fun)}'")
                # noinspection PyUnresolvedReferences
                sig = signature(fun.__call__)
                self.fhosh = fhosh
            else:
                self.fhosh = f2hosh(fun) if fhosh is None else fhosh
                sig = signature(fun)

            # Separate positional parameters from named parameters looking at 'f' signature.
            self.args, self.kwargs = handle_args(sig, applied_args, applied_kwargs)
            self.requirements = {k: v for k, v in sorted((self.args | self.kwargs).items())}
        else:
            raise Exception(f"Cannot apply type '{type(f)}'.")
        self._fun = fun
        # Requirements (dependencies stub) are alphabetically sorted to ensure we keep the same resulting hosh no matter in which order the parameters are defined in the function.

    @property
    def ahosh(self):
        return self.fhosh.rev  # 'f' identified as an appliable function

    def __call__(self, *out):
        from hdict.entry.applyout import applyOut
        return applyOut(self, out)

    @property
    def finished(self):
        return self._finished

    def finish(self, data):
        if self.finished:
            raise Exception(f"Cannot finish an application twice.")
        if isinstance(self.f, field) and not self.f.finished:
            self.f.finish(data)
        if self.fhosh is None:
            self.fhosh = self.f.hosh
        reqs = self.requirements
        for kreq, req in reqs.items():
            if isinstance(req, (apply, field)) and not req.finished:
                req.finish(data)
        self._finished = True

    def clone(self):
        return apply(self)

    @property
    def hosh(self):
        if not self.finished:
            raise Exception(f"Cannot know apply.hosh before finishing object '{self.fhosh}'.")
        if self._hosh is None:
            self._hosh = reduce(mul, chain(hoshes(self.requirements.values()), [self.ahosh]))
        return self._hosh

    @property
    def value(self):
        if self._value is Unevaluated:
            if not self.finished:
                raise Exception(f"Cannot access apply.value before finishing object '{self.fhosh}'.")
            self._value = self._fun(*(x.value for x in self.args.values()), **{k: v.value for k, v in self.kwargs})
        return self._value

    @property
    def fun(self):
        return self._fun

    @property
    def isevaluated(self):
        return self._value is not Unevaluated

    def __repr__(self):
        if not self.isevaluated:
            from hdict.entry.default import default
            lst = []
            for depk, depv in self.requirements.items():
                if isinstance(depv, (field, default)) or not depv.isevaluated:
                    lst.append(f"{depk}={repr(depv)}")
                else:
                    lst.append(str(depk))
            return f"λ({' '.join(lst)})"
        return repr(self._value)

    def multifield(self: tuple, v: [list, IndexedDict, "apply"]):
        pass
        # SubVal(self, item)
        # sorted(keys())    # Hoshes are assigned to each output according to the alphabetical order of the keys.
        # hosh[:n]
