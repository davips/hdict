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
from hosh import Hosh

from hdict.content.argument import AbsBaseArgument
from hdict.content.entry import AbsEntry
from hdict.content.aux_value import v2hosh


class value(AbsBaseArgument, AbsEntry):
    """
    Wrapper for any Python object except AbsAny instances

    >>> x = 5
    >>> from hdict.content.value import value
    >>> v = value(x, "1234567890123456789012345678901234567890")
    >>> v
    5
    >>> v.hosh.id
    '1234567890123456789012345678901234567890'

    """

    isevaluated = True

    def __init__(self, val: object, hosh: Hosh | str = None, hdict=None):
        """

        Args:
            val:
            hosh:
            hdict:  optional reference to the object if it has a hdict counterpart (e.g.: pandas DF)
        """
        from hdict.abs import AbsAny

        if isinstance(val, AbsAny):  # pragma: no cover
            raise Exception(f"Cannot handle objects of type '{type(val).__name__}' as raw values for hdict.")
        self.value = self._value = val
        if isinstance(hosh, str):
            hosh = Hosh.fromid(hosh)
        self.hosh = v2hosh(self.value) if hosh is None else hosh
        self.hdict = hdict

    def __repr__(self):
        return repr(self.value)
