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

from hdict.content.entry import AbsEntry


@dataclass
class SubValue(AbsEntry):
    """
    A field containing part of other field

    >>> from hdict import value
    >>> v = SubValue(value([3]), 0, 1)
    >>> v
    [3]→0
    >>> v.value
    3
    >>> v
    3
    """

    parent: AbsEntry
    index: int
    n: int
    source: str = None

    # target: str = None

    def __post_init__(self):
        self.hosh = self.parent.hosh[self.index, self.n]

    @property
    def value(self):
        from hdict.content.entry import Unevaluated

        if isinstance(self._value, Unevaluated):
            value = self.parent.value
            if isinstance(value, (list, tuple)):
                if len(value) < self.n:  # pragma: no cover
                    raise Exception(f"Number of output fields ('{self.n}') should not exceed number of resulting list elements ('{len(value)}').")
                self._value = value[self.index]
            elif isinstance(value, dict):
                if len(value) != self.n:  # pragma: no cover
                    raise Exception(f"Number of output fields ('{self.n}') should match number of resulting dict entries ('{len(value)}').")
                if self.source:
                    self._value = value[self.source]
                self._value = list(sorted(value.items()))[self.index][1]
            else:  # pragma: no cover
                raise Exception(f"Cannot infer subvalue '{self.index}' of type '{type(value).__name__} {value}.")
        return self._value

    def __repr__(self):
        if self.isevaluated:
            return repr(self._value)
        # t = self.parent if self.target is None else self.target
        return f"{self.parent}→{str(self.index if self.source is None else self.source)}"
