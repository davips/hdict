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
from random import Random

from hosh import Hosh

from hdict.content.abs.any import AbsAny
from hdict.content.value import value
from hdict.content.abs.sampling import withSampling
from hdict.content.abs.variable import AbsVariable
from hdict.hoshfication import v2hosh


class default(AbsVariable, withSampling):
    def __init__(self, val: object | AbsVariable | value, hosh: Hosh | str = None, _sampleable=None):
        from hdict import value, field, sample
        if not isinstance(val, (value, field, sample)) and isinstance(val, AbsAny):  # pragma: no cover
            raise Exception(f"Cannot use '{type(val)}' as a default function parameter.")
        self.value = val
        self._hosh = Hosh.fromid(hosh) if isinstance(hosh, str) else hosh
        self.isevaluated = True
        self.sampleable = val.sampleable if _sampleable is None and isinstance(val, (AbsVariable, value)) else _sampleable

    def sample(self, rnd: int | Random = None):
        if not self.sampleable:
            return self
        return default(self.value.sample(rnd), self.hosh, _sampleable=False)

    @property
    def hosh(self):
        if self._hosh is None:
            self._hosh = v2hosh(self.value)
        return self._hosh

    def __repr__(self):
        return f"default({repr(self.value)})"
