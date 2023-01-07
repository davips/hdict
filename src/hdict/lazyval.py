from functools import reduce, cached_property
from itertools import chain
from operator import mul

from hdict import apply
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
    >>> v = LazyVal(apply(f), {}, {"a": StrictVal(x), "b": StrictVal(y)})
    >>> v
    λ(a b)
    >>> v2 = LazyVal(apply(f), {"a": v}, {"b": StrictVal(y)})
    >>> v2
    λ(a=λ(a b) b)
    >>> v.value
    78125
    >>> v
    78125
    """
    _value = unevaluated

    def __init__(self, appl: apply, value_deps: IndexedDict[str, AbsVal], field_deps: dict[str, AbsVal]):
        self.args, self.kwargs =  value_deps, field_deps
        self.fhosh = appl.hosh
        if isinstance(appl.f,str)

    @cached_property
    def dependencies(self):
        return self.args | self.kwargs

    @cached_property
    def hosh(self):  # REMINDER: id of 'f(x,y,z)' is 'xyzf'
        return reduce(mul, chain(hoshes(self.dependencies.values()), [self.fhosh]))

    @property
    def isevaluated(self):
        return self._value is not unevaluated

    @property
    def value(self):
        if self._value is unevaluated:
            self.evaluate()
        return self._value

    def evaluate(self):
        args = (x.value for x in self.args.values())
        kwargs = {k: v.value for k, v in self.kwargs.items()}
        self._value = self.f(*args, **kwargs)

    def __repr__(self):
        if not self.isevaluated:
            lst = (str(field) + ("" if dep.isevaluated else f"={repr(dep)}") for field, dep in self.dependencies.items())
            return f"λ({' '.join(lst)})"
        return repr(self.value)
