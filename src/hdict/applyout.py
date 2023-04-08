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

from hdict.abs import AbsAny
from hdict.content.argument.apply import apply


@dataclass
class ApplyOut(AbsAny):
    """Wrapper for 'apply' to append the output field(s)"""

    nested: apply
    out: [str | tuple[str, str]]

    def sample(self, rnd: int | Random = None):
        if not self.nested.sampleable:
            return self
        return ApplyOut(self.nested.sample(rnd), self.out)

    @property
    def sampleable(self):
        return self.nested.sampleable

    def __rrshift__(self, left):
        from hdict import hdict, frozenhdict

        if isinstance(left, dict) and not isinstance(left, (hdict, frozenhdict)):
            return hdict(left) >> self
        return NotImplemented  # pragma: no cover

    def __rmul__(self, left):
        from hdict import hdict, frozenhdict
        from hdict.expr import Expr

        if isinstance(left, dict) and not isinstance(left, (hdict, frozenhdict)):
            return Expr(left, self)
        return NotImplemented  # pragma: no cover

    def __rshift__(self, right):
        from hdict.expr import Expr

        # REMINDER: dict includes hdict/frozenhdict.
        if isinstance(right, (dict, ApplyOut)):
            return Expr(self, right)
        return NotImplemented  # pragma: no cover

    def __mul__(self, right):
        return self.__rshift__(right)

    def __repr__(self):
        return f"{self.out}={repr(self.nested)}"
