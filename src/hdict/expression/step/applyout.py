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

from hdict.content.argument.apply import apply
from hdict.expression.step.step import AbsStep


@dataclass
class ApplyOut(AbsStep):
    """
    Wrapper for 'apply' to append the output field(s)

    >>> from hdict import cache, apply, sample
    >>> e = dict() * apply(lambda x: x*2, x=sample(1,2,3,...,9)).a * (cache({}) >> dict(s=sample(1,2,3,...,9)))
    >>> e.show(colored=False)
    ⦑{} » a=λ(x=~[1 2 .+. 9]) » ↑↓`dict` » {s: "~[1 2 .+. 9]"}⦒
    >>> e.steps[0].steps[1].sampleable
    True
    >>> (~e).show(colored=False)
    {
        a: ↑↓ cached at `dict`·,
        s: 7,
        _id: E3YKpiQXWwK1AZh9BcqI7AoamBanxAr1GAOeJudy,
        _ids: {
            a: ygBt7xenihJVMnjwJxN6Z1H7HYnrET04zEYTRKD3,
            s: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf
        }
    }
    """

    nested: apply
    out: [str | tuple[str, str]]

    def sample(self, rnd: int | Random = None):
        if not self.nested.sampleable:
            return self
        return ApplyOut(self.nested.sample(rnd), self.out)

    @property
    def sampleable(self):
        return self.nested.sampleable

    def __repr__(self):
        return f"{self.out}={repr(self.nested)}"
