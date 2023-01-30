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

from hdict.entry.abs.abscontent import AbsContent
from hdict.hoshfication import v2hosh
from hosh import Hosh


class default:
    def __init__(self, value: object, hosh: Hosh | str = None, hdict=None):
        from hdict.entry.field import field
        if isinstance(value, AbsContent) and not isinstance(value, field):
            raise Exception(f"Can only nest 'field' or ordinary values inside a 'default' object: '{type(value)}")
        self.value = value
        self._hosh = Hosh.fromid(hosh) if isinstance(hosh, str) else hosh
        self.hdict = hdict
        self.isevaluated = True

    @property
    def hosh(self):
        if self._hosh is None:
            self._hosh = v2hosh(self.value)
        return self._hosh

    def __repr__(self):
        return f"default({repr(self.value)})"
