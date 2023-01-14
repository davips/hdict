from dataclasses import dataclass
from random import Random

from lange.tricks import list2progression

from hdict.absval import AbsVal
from hdict.lazyval import LazyVal


class absparam:
    obj: AbsVal | object
    ispositional: bool

    @property
    def isevaluated(self):
        return self.obj.isevaluated

    @property
    def value(self):
        return self.obj.value

    @property
    def hosh(self):
        return self.obj.hosh

    def __hash__(self):
        return hash(self.obj)


@dataclass
class field(absparam):
    obj: AbsVal | object
    ispositional: bool = None


@dataclass
class val(absparam):
    obj: AbsVal | object
    ispositional: bool = None


@dataclass
class default(absparam):
    obj: AbsVal | object
    ispositional: bool = None


class sample(absparam):  # TODO: finish
    """
    >>> (s := sample(1, 2, 3, ..., 9).values)
    [1 2 .+. 9]
    >>> s.l
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> (s := sample(2, 4, 8, ..., 1024).values)
    [2 4 .*. 1024]
    >>> s.l
    [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

    Args:
        *values:
        rnd:
        maxdigits:
    """
    obj: object

    def __init__(self, *values: list[int | float], rnd: Random = Random(0), maxdigits=28, ispositional: bool = None):
        self.rnd, self.ispositional = rnd, ispositional
        # minor TODO reject infinite values
        # minor TODO optimize by using new lazy item access of future 'lange'
        self.values = list2progression(values, maxdigits=maxdigits).l

    def __iter__(self):
        while True:
            yield self.rnd.choice(self.values)

    def add_dependent(self, dependent: LazyVal):
        0
