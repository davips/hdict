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

from hdict.abs import AbsAny
from hdict.content.argument.apply import apply


@dataclass
class ApplyOut(AbsAny):
    """Wrapper for 'apply' to append the output field(s)"""
    nested: apply
    out: [str | tuple[str, str]]

    def __rrshift__(self, other):
        from hdict import hdict, frozenhdict

        if isinstance(other, dict) and not isinstance(other, (hdict, frozenhdict)):
            return hdict() >> other >> self
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other):
        from hdict import hdict

        # REMINDER: dict includes hdict/frozenhdict.
        if isinstance(other, (dict, ApplyOut)):
            return hdict() >> self >> other
        return NotImplemented  # pragma: no cover

    def __repr__(self):
        return f"{self.out}={repr(self.nested)}"
