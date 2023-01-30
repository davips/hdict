#  Copyright (c) 2023. Davi Pereira dos Santos
#  This file is part of the hdict project.
#  Please respect the license - more about this in the section (*) below.
#
#  hdict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  hdict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with hdict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#

from dataclasses import dataclass
from random import Random

from lange.tricks import list2progression

from hdict.entry.abs.abscontent import AbsContent
from hdict.entry.abs.abssampleable import AbsSampleable


@dataclass
class sample(AbsContent, AbsSampleable):
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

    def __init__(self, *values: list[int | float], rnd: int | Random = 0, maxdigits=28):
        self.rnd = rnd
        # minor TODO: reject infinite values; optimize by using new lazy item access of future 'lange'
        self.values = list2progression(values, maxdigits=maxdigits).l

    def sample(self, rnd: int | Random = None):
        from hdict.entry.value import value
        if rnd is None:
            rnd = self.rnd
        if isinstance(rnd, int):
            rnd = Random(rnd)
        if not isinstance(rnd, Random):
            raise Exception(f"Sampling needs an integer seed or a Random object.")
        return value(rnd.choice(self.values))
