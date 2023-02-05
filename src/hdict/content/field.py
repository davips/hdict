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

from hdict.content.abs.abscloneable import AbsCloneable
from hosh import Hosh


class field(AbsCloneable):
    """
    Pointer to a field
    """

    content = None

    def __init__(self, name: str, hosh: Hosh | str = None):
        self.name = name
        self._hosh = Hosh.fromid(hosh) if isinstance(hosh, str) else hosh

    def finish(self, data):
        """
        >>> d = {"a": field("b"), "b": field("c"), "c": 5}
        >>> d
        {'a': field('b'), 'b': field('c'), 'c': 5}
        >>> d["a"].finish(d)
        >>> d
        {'a': c, 'b': c, 'c': 5}
        >>> d["a"].value
        5
        """
        if self.content is not None:  # pragma: no cover
            raise Exception(f"Cannot finish a field pointer twice. name: {self.name}; hosh: {self.hosh}")
        if self.name not in data:  # pragma: no cover
            raise Exception(f"Missing field '{self.name}'")
        self.content = data[self.name]
        if isinstance(self.content, AbsCloneable) and not self.content.finished:
            self.content.finish(data)
        self._finished = True

    @property
    def hosh(self):
        if self.content is None:  # pragma: no cover
            raise Exception(f"Cannot know hosh before finishing pointer to field '{self.name}'.")
        if self._hosh is None:
            self._hosh = self.content.hosh
        return self._hosh

    @property
    def value(self):
        from hdict.content.abs.abscontent import AbsContent

        if self.content is None:  # pragma: no cover
            raise Exception(f"Cannot access value before finishing pointer to field '{self.name}'.")
        return self.content.value if isinstance(self.content, AbsContent) else self.content

    @property
    def isevaluated(self):  # pragma: no cover
        return self.content and self.content.isevaluated

    def clone(self):
        return field(self.name, self._hosh)

    def __repr__(self):
        if self.content is None:
            txt = f"field('{self.name}'"
            txt += ")" if self._hosh is None else ", '{self._hosh}')"
            return txt
        return repr(self.content) if isinstance(self.content, field) else self.name
