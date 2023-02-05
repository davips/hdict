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

from hdict.content.abs.abssampleable import AbsSampleable


class pipeline(AbsSampleable):
    def __init__(self, *args, _previous: list = None):
        self.steps = _previous.copy() if _previous else []
        self.steps.extend(args)

    def sample(self, rnd: int | Random = None):
        newsteps = [(step.sample(rnd) if isinstance(step, AbsSampleable) else step) for step in self.steps]
        return pipeline(_previous=newsteps)

    def __rshift__(self, other):
        from hdict import apply
        from hdict.content.applyout import applyOut

        if isinstance(other, pipeline):
            return pipeline(*other.steps, _previous=self.steps)
        if isinstance(other, (apply, applyOut)):
            return pipeline(other, _previous=self.steps)
        return NotImplemented  # pragma: no cover
