from dataclasses import dataclass
from random import Random

from lange.tricks import list2progression

from hdict.entry.abscontent import AbsContent


@dataclass
class sample(AbsContent):
    """
    >>> (s := sample(1, 2, 3, ..., 9).values)
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> (s := sample(2, 4, 8, ..., 1024).values)
    [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

    Args:
        *values:
        rnd:
        maxdigits:
    """
    obj: object

    def __init__(self, *values: list[int | float], rnd: Random = Random(0), maxdigits=28):
        self.rnd = rnd
        # minor TODO reject infinite values
        # minor TODO optimize by using new lazy item access of future 'lange'
        self.values = list2progression(values, maxdigits=maxdigits).l

    def __iter__(self):
        while True:
            yield self.rnd.choice(self.values)
