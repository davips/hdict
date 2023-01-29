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

from hdict.entry.abscontent import AbsContent


class SubVal(AbsContent):
    def __init__(self, parent: AbsContent, item: [int, str], hosh: Hosh):
        self.parent, self.item, self.hosh = parent, item, hosh
        self.isevaluated = self.parent.isevaluated
        self.__repr__ = self.parent.__repr__

    @property
    def value(self):
        # noinspection PyUnresolvedReferences
        return self.parent.value[self.item]
