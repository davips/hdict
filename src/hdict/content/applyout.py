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
from random import Random

from hdict.content.abs.abscontent import AbsContent
from hdict.content.abs.abssampleable import AbsSampleable
from hdict.content.apply import apply


@dataclass
class applyOut(AbsContent, AbsSampleable):
    nested: apply
    out: [str | tuple[str, str]]

    def __post_init__(self):
        outs = [self.out] if isinstance(self.out, str) else self.out
        keys = self.nested.requirements.keys()

    def sample(self, rnd: int | Random = None):
        return applyOut(self.nested.sample(rnd), self.out)

    def __rshift__(self, other):
        from hdict.pipeline import pipeline

        if isinstance(other, (pipeline, applyOut)):
            return pipeline(self, other)
        return NotImplemented  # pragma: no cover

    #
    #     Traceback (most recent call last):
    #   File "/home/davi/.config/JetBrains/PyCharmCE2022.3/scratches/scratch_14.py", line 44, in <module>
    #     du = dumps(d, protocol=5)
    # TypeError: 'applyOut' object is not callable
    # def __reduce__(self):
    #     print(111111111111111111)
