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

from hdict.content.abs.any import AbsAny
from hdict.content.abs.sampling import withSampling
from hdict.content.apply import apply


@dataclass
class applyOut(AbsAny, withSampling):
    """Wrapper for 'apply' to append the output field(s)"""
    nested: apply
    out: [str | tuple[str, str]]
    caches: tuple
    _sampleable = None

    @property
    def sampleable(self):
        if self._sampleable is None:
            self._sampleable = self.nested.sampleable
        return self._sampleable

    # def __post_init__(self):
    #     outs = [self.out] if isinstance(self.out, str) else self.out
    #     keys = self.nested.requirements.keys()

    def sample(self, rnd: int | Random = None):
        if not self.sampleable:
            return self
        return applyOut(self.nested.sample(rnd), self.out, self.caches)

    def cached(self, *caches):
        if not caches:  # pragma: no cover
            raise Exception(f"Missing at least one dict-like object for caching.")
        nested = "TODO"  # apply(f,self.nested.args
        return self
        return applyOut(nested, self.out, caches)

    def __rrshift__(self, other):
        from hdict import hdict, frozenhdict

        if isinstance(other, dict) and not isinstance(other, (hdict, frozenhdict)):
            return hdict() >> other >> self
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other):
        from hdict.pipeline import pipeline

        # REMINDER: dict includes hdict/frozenhdict.
        if isinstance(other, (dict, applyOut, pipeline)):
            return pipeline(self, other)
        return NotImplemented  # pragma: no cover

    def __repr__(self):
        return f"{self.out}={repr(self.nested)}"

    #
    #     Traceback (most recent call last):
    #   File "/home/davi/.config/JetBrains/PyCharmCE2022.3/scratches/scratch_14.py", line 44, in <module>
    #     du = dumps(d, protocol=5)
    # TypeError: 'applyOut' object is not callable
    # def __reduce__(self):
    #     print(111111111111111111)
