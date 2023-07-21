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
from typing import Callable

from hosh import Hosh

from hdict.abs import AbsAny


@dataclass
class Unevaluated:
    pass


class AbsEntry(AbsAny):
    """
    hdict final entry at internal level: value*, SubValue, Closure

    *value also inherits AbsBaseArgument because 'value' objects have a meaning outside of hdict (external level)
    """

    value: object | Callable  # REMINDER: 'callable' is here for appliable contents, like storing a raw lambda
    hosh: Hosh
    _value = Unevaluated()

    @property
    def id(self):  # pragma: no cover
        return self.hosh.id

    def evaluate(self):
        _ = self.value

    @property
    def isevaluated(self):
        """
        >>> from hdict import apply, frozenhdict
        >>> from hdict.content.entry.closure import Closure
        >>> Closure(apply(lambda x, y: x + y), {"x": 3, "y": 5}, [], frozenhdict).isevaluated
        False
        """
        return not isinstance(self._value, Unevaluated)
