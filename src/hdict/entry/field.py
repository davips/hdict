from functools import cached_property

from hdict.entry import Unfilled
from hdict.entry.absnest import AbsNest
from hosh import Hosh


class field(AbsNest):
    """
    Pointer to a field
    """

    def __init__(self, name: str, hosh: Hosh = None):
        self.name, self._hosh = name, hosh

    @property
    def hosh(self):
        if self._hosh is None:
            self._hosh = self.content.hosh
        return self._hosh

    @property
    def value(self):
        return self.content.value

    def clone(self, hosh: Hosh = None):
        new = field(self.name, hosh=hosh or self.hosh)
        new._content = Unfilled
        return new

    def __repr__(self):
        txt = f"field(name='{self.name}'"
        txt += ")" if self._hosh is None else ", hosh='{self._hosh}')"
        return txt
