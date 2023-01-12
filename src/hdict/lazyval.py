from functools import reduce, cached_property
from itertools import chain
from operator import mul

from hdict.apply import apply
from hdict.param import val
from hdict.absval import AbsVal
from hdict.indexeddict import IndexedDict
from hosh.misc import hoshes


class unevaluated:
    pass


Unevaluated = unevaluated()


class LazyVal(AbsVal):
    """
    >>> x, y = 5, 7
    >>> f = lambda a, b: a**b
    >>> from hdict.strictval import StrictVal
    >>> v = LazyVal(apply(f), {"a": val(StrictVal(x)), "b": val(StrictVal(y))})
    >>> v
    λ(a b)
    >>> v2 = LazyVal(apply(f), {"a": v, "b": val(StrictVal(y))})
    >>> v2
    λ(a=λ(a b) b)
    >>> v.value
    78125
    >>> v
    78125
    """
    _value = unevaluated

    def __init__(self, appl: apply, dependencies: IndexedDict[str, AbsVal]):
        self._dependencies = dependencies
        self.fhosh = appl.hosh
        self._f = appl.f

    @cached_property
    def dependencies(self):  # REMINDER: returned value differs from provided 'dependencies': 'f' as 'str' is removed here.
        if self._f in self._dependencies:
            self._f = self.dependencies.pop(self._f)
            if isinstance(self._f, str):
                raise Exception(f"'LazyVal.dependencies' called before filling 'deps_stub'.")
        return self._dependencies

    @cached_property
    def hosh(self):  # REMINDER: id of 'f(x,y,z)' is 'xyzf'
        return reduce(mul, chain(hoshes(self.dependencies.values()), [self.fhosh]))

    # @property
    # def f(self):
    #     return self._f.value

    @property
    def isevaluated(self):
        return self._value is not unevaluated

    @property
    def value(self):
        if self._value is unevaluated:
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
        if not self.isevaluated:
            lst = (str(field) + ("" if dep.isevaluated else f"={repr(dep)}") for field, dep in self.dependencies.items())
            return f"λ({' '.join(lst)})"
        return repr(self.value)
