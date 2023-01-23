from functools import reduce, cached_property
from inspect import isfunction
from inspect import signature
from itertools import chain
from operator import mul
from typing import Union

from hdict.entry.handling import Unevaluated, handle_args
from hdict.entry.value import value
from hdict.entry.absarg import AbsArg
from hdict.entry.field import field
from hdict.hoshfication import f2hosh
from hdict.indexeddict import IndexedDict
from hosh import Hosh
from hosh.misc import hoshes


class apply(AbsArg):
    """
    >>> from hdict import apply, value
    >>> f = lambda a, b: a**b
    >>> v = apply(f, value(5), b=value(7))
    >>> v
    λ(a b)
    >>> g = lambda x, y: x**y
    >>> apply(g, x=v, y=value(7))

    >>> v2 = apply(f, a=v, b=value(7))
    >>> v2
    λ(a=λ(a b) b)
    >>> v.entry
    78125
    >>> v2.entry
    78125

    >>> f = lambda a,b, c=1,d=2,e=13: 0
    >>> apply(f).entry, apply(f).kwargs
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
    >>> f = lambda a,b, *entry, c=1,d=2,e=13, **kwargs: 0
    >>> apply(f,3,4,5,6,7,8).input
    {'a': val(obj=3, ispositional=True), 'b': val(obj=4, ispositional=True), 'c': val(obj=5, ispositional=True), 'd': val(obj=6, ispositional=True), 'e': val(obj=7, ispositional=True), 5: val(obj=8, ispositional=True)}
    >>> apply(f,x=3,e=4,d=5,c=6,b=7,a=8).input
    {'a': val(obj=8, ispositional=True), 'b': val(obj=7, ispositional=True), 'c': val(obj=6, ispositional=False), 'd': val(obj=5, ispositional=False), 'e': val(obj=4, ispositional=False), 'x': val(obj=3, ispositional=False)}
    >>> apply(f,3,c=77,x=5).input
    {'a': val(obj=3, ispositional=True), 'b': field(obj='b', ispositional=True), 'c': val(obj=77, ispositional=False), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False), 'x': val(obj=5, ispositional=False)}
    >>> apply(f,b=77,x=5).input
    {'a': field(obj='a', ispositional=True), 'b': val(obj=77, ispositional=True), 'c': default(obj=1, ispositional=False), 'd': default(obj=2, ispositional=False), 'e': default(obj=13, ispositional=False), 'x': val(obj=5, ispositional=False)}

    """
    out = None
    _value = Unevaluated

    # TODO: allow_partial
    #     TODO multifield
    def __init__(self, f: Union[callable, "apply", field], *applied_args, allow_partial=False, fhosh: Hosh = None, ispositional: bool = None, **applied_kwargs):
        self.allow_partial, self.ispositional = allow_partial, ispositional
        self._dependencies: IndexedDict[str, AbsArg] = {}  # Pairs: «fparameter, farg»
        if isinstance(f, apply):  # cloning mode
            if applied_args or applied_kwargs:
                raise Exception("Providing an 'apply' object as 'f' (i.e., in cloning mode) requires no 'applied_args' nor 'applied_kwargs'.")
            fargs = f.args
            fkwargs = f.kwargs
            f = f.f
        elif isinstance(f, field):
            fargs = applied_args
            fkwargs = applied_kwargs
            self._dependencies[f.name] = f
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

    @cached_property
    def requirements(self):
        return self.args | self.kwargs

    def clone(self, allow_partial=None, hosh: Hosh = None):
        if allow_partial is None:
            allow_partial = self.allow_partial
        if hosh is None:
            hosh = self.hosh
        return apply(self, allow_partial=allow_partial, hosh=hosh)

    def __call__(self, *out):
        new = self.clone()
        new.out = out
        return new

    @cached_property
    def dependencies(self):
        if isinstance(self._f, field):
            self._f = self._dependencies.pop(self._f.name)
            _ = self._f.nested  # This is to ensure an exception will be raised if nested not ready yet.
        # Dependencies are alphabetically sorted to ensure we keep the same resulting hosh no matter in which order the parameters are defined in the function.
        for k, v in sorted(self.requirements.items()):
            self._dependencies[k] = v
        return self._dependencies

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
        args, kwargs = [], {}
        for k, v in self.dependencies.items():
            if v.ispositional:
                args.append(v.obj)
            else:
                kwargs[k] = v.obj
        self._value = self._f(*args, **kwargs)

    def __repr__(self):
        print(self.isevaluated, list([k,type(d)] for k,d in self.dependencies.items()))
        if not self.isevaluated:
            # TODO: check if dep labels refer to f params or hdict fields
            lst = (str(depk) + ("" if depv.isevaluated else f"={repr(depv)}") for depk, depv in self.dependencies.items())
            return f"λ({' '.join(lst)})"
        return repr(self.value)


    def multifield(k: tuple, v: [list, IndexedDict, "apply"]):
        pass
        # SubVal(self, item)
        # sorted(keys())    # Hoshes are assigned to each output according to the alphabetical order of the keys.
        # hosh[:n]
