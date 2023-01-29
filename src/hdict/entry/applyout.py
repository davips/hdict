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

from hdict.entry.abscontent import AbsContent
from hdict.entry.apply import apply


@dataclass
class applyOut(AbsContent):
    apply: apply
    out: [str]

    def __post_init__(self):
        self.f = self.apply.f
        self.fun = self.apply.fun
        self.fhosh = self.apply.fhosh
        self.ahosh = self.apply.ahosh
        self.args = self.apply.args
        self.kwargs = self.apply.kwargs
        self.requirements = self.apply.requirements
        # noinspection PyTypeChecker
        self.fun = self.apply.fun
        self.__repr__ = self.apply.__repr__

    @property
    def hosh(self):
        return self.apply.hosh

    @property
    def value(self):
        return self.apply.value

    @property
    def isevaluated(self):
        return self.apply.isevaluated
