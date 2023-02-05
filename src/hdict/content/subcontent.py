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
from functools import cached_property

from hdict.content.abs.abscloneable import AbsCloneable
from hdict.content.abs.abscontent import AbsContent
from hosh import Hosh


class subcontent(AbsCloneable):
    content = None
    _finished = False

    def __init__(self, parent: AbsContent, index: int, n: int, source: str = None, hosh: Hosh = None):
        self.parent, self.index, self.n, self.source, self._hosh = parent, index, n, source, hosh

    @property
    def requirements(self):
        from hdict import apply

        return self.parent.requirements if isinstance(self.parent, apply) else {}

    @property
    def hosh(self):
        if self._hosh is None:
            h = self.parent.hosh
            self._hosh = h[self.index : self.n]
        return self._hosh

    @property
    def isevaluated(self):
        return self.parent.isevaluated

    @cached_property
    def value(self):
        value = self.parent.value
        if isinstance(value, list):
            if len(value) < self.n:  # pragma: no cover
                raise Exception(f"Number of output fields ('{self.n}') should not exceed number of resulting list elements ('{len(value)}').")
            return value[self.index]
        if isinstance(value, dict):
            if len(value) != self.n:  # pragma: no cover
                raise Exception(f"Number of output fields ('{self.n}') should match number of resulting dict entries ('{len(value)}').")
            if self.source:
                return value[self.source]
            return list(sorted(value.items()))[self.index][1]
        else:  # pragma: no cover
            raise Exception(f"Cannot infer subvalue '{self.index}' of type '{type(value)} {value}.")

    def clone(self, parent=None):
        parent = parent or (self.parent.clone() if isinstance(self.parent, AbsCloneable) else self.parent)
        return subcontent(parent, self.index, self.n, self.source, self._hosh)

    def finish(self, data):
        """
        >>> from hdict import value
        >>> subcontent(value([3]), 0,1)
        3
        """
        if self.finished:  # pragma: no cover
            raise Exception(f"Cannot finish a subcontent twice.")
        if isinstance(self.parent, AbsCloneable) and not self.parent.finished:
            self.parent.finish(data)
        self._finished = True

    def __repr__(self):
        if self.isevaluated:
            return repr(self.value)
        return f"{self.parent}→{str(self.index if self.source is None else self.source)}"
