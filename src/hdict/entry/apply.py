from functools import reduce, cached_property
from inspect import isfunction
from inspect import signature
from itertools import chain
from operator import mul
from typing import Union

from hdict.entry import Unfilled
from hdict.entry.absnest import AbsNest
from hdict.entry.handling import Unevaluated, handle_args
from hdict.entry.value import value
from hdict.entry.abscontent import AbsContent
from hdict.entry.field import field
from hdict.hoshfication import f2hosh
from hdict.indexeddict import IndexedDict
from hosh import Hosh
from hosh.misc import hoshes


class apply(AbsNest):
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
    >>> v.value, v2
    (78125, λ(a b))
    >>> v2.value, v2
    (17763568394002504646778106689453125, 17763568394002504646778106689453125)

    >>> f = lambda a,b, c=1,d=2,e=13: 0
    >>> apply(f).requirements
    {'a': field(name='a'), 'b': field(name='b'), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> apply(f,3).requirements
    {'a': 3, 'b': field(name='b'), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4).requirements
    {'a': 3, 'b': 4, 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5,6).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': default(13)}
    >>> apply(f,3,4,5,6,7).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7}
    >>> apply(f,d=5).requirements
    {'a': field(name='a'), 'b': field(name='b'), 'c': default(1), 'd': 5, 'e': default(13)}
    >>> f = lambda a,b, *entry, c=1,d=2,e=13, **kwargs: 0
    >>> apply(f,3,4,5,6,7,8).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7, _5: 8}
    >>> apply(f,x=3,e=4,d=5,c=6,b=7,a=8).requirements
    {'a': 8, 'b': 7, 'c': 6, 'd': 5, 'e': 4, 'x': 3}
    >>> apply(f,3,c=77,x=5).requirements
    {'a': 3, 'b': field(name='b'), 'c': 77, 'd': default(2), 'e': default(13), 'x': 5}
    >>> apply(f,b=77,x=5).requirements
    {'a': field(name='a'), 'b': 77, 'c': default(1), 'd': default(2), 'e': default(13), 'x': 5}
    """
    out = None
    _dependencies: IndexedDict[str, AbsContent] = None  # Pairs: «fparameter, farg»
    _value = Unevaluated
    name = "apply"

    #     TODO multifield
    def __init__(self, f: Union[callable, "apply", field], *applied_args, fhosh: Hosh = None, **applied_kwargs):
        if isinstance(f, apply):  # "clone" mode
            if applied_args or applied_kwargs:
                raise Exception("Providing an 'apply' object as 'f' (i.e., in cloning mode) requires no 'applied_args' nor 'applied_kwargs'.")
            fargs = f.args
            fkwargs = f.kwargs
            f = f.f
            self._dependencies = Unfilled
        elif isinstance(f, AbsContent):  # "function will be provided by hdict" mode
            f = lambda *args, **kwargs: f.value(*args, **kwargs)
            fargs = applied_args
            fkwargs = applied_kwargs
        elif callable(f):
            if not isfunction(f):  # "not function" means "method of a custom callable"
                if not hasattr(f, "__call__"):
                    raise Exception(f"Cannot infer method to apply non custom callable type '{type(f)}'.")
                if not hasattr(f, "hosh"):
                    raise Exception(f"Missing 'hosh' attribute while applying custom callable class '{type(f)}'")
                # noinspection PyUnresolvedReferences
                sig = signature(f.__call__)
            else:
                if fhosh is None:
                    fhosh = f2hosh(f)
                sig = signature(f)

            # Separate positional parameters from named parameters looking at 'f' signature.
            fargs, fkwargs = handle_args(sig, applied_args, applied_kwargs)
        else:
            raise Exception(f"Cannot apply type '{type(f)}'.")
        self._f = f
        self.fhosh = fhosh  # 'f' identified as a value
        self.ahosh = fhosh.rev  # 'f' identified as an appliable function
        self.args = fargs
        self.kwargs = fkwargs
        # Requirements (dependencies stub) are alphabetically sorted to ensure we keep the same resulting hosh no matter in which order the parameters are defined in the function.
        self.requirements = {k: v for k, v in sorted((fargs | fkwargs).items())}

    def clone(self, hosh: Hosh = None):
        if hosh is None:
            hosh = self.hosh
        return apply(self, hosh=hosh)

    def __call__(self, *out):
        new = self.clone()
        new.out = out
        return new

    @property
    def dependencies(self):
        return self.content

    @cached_property
    def hosh(self):  # REMINDER: id of 'f(b,c,a)' is 'abcf'
        return reduce(mul, chain(hoshes(self.dependencies.values()), [self.fhosh]))

    # @property
    # def f(self):
    #     return self._f.entry

    @property
    def isevaluated(self):
        return self._value is not Unevaluated

    @property
    def value(self):
        if self._value is Unevaluated:
            self.evaluate()
        return self._value

    def evaluate(self):
        self._value = self._f(*(x.value for x in self.args.values()), **{k: v.value for k, v in self.kwargs})

    def __repr__(self):
        if not self.isevaluated:
            # TODO: check if dep labels refer to f params or hdict fields
            lst = (str(depk) + ("" if depv.isevaluated else f"={repr(depv)}") for depk, depv in self.requirements.items())
            return f"λ({' '.join(lst)})"
        return repr(self.value)

    def multifield(k: tuple, v: [list, IndexedDict, "apply"]):
        pass
        # SubVal(self, item)
        # sorted(keys())    # Hoshes are assigned to each output according to the alphabetical order of the keys.
        # hosh[:n]
