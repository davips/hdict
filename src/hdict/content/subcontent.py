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
from hdict.content.abs.appliable import AbsAppliable
from hdict.content.abs.requirements import withRequirements


class subcontent(AbsAppliable, withRequirements):
    """
    >>> from hdict import value
    >>> subcontent(value([3]), 0,1)
    3
    """

    def __init__(self, parent: AbsAppliable, index: int, n: int, source: str = None):
        from hdict import apply
        self.parent, self.index, self.n, self.source = parent, index, n, source
        if isinstance(parent, apply):
            self.fargs, self.fkwargs = parent.fargs, parent.fkwargs
            self.appliable = parent.appliable
            self.ahosh = parent.ahosh
            self.isfield = parent.isfield
        else:
            # nested subcontent
            raise Exception(f"")  # TODO
            self.fargs, self.fkwargs = {}, {}
            self.appliable = None
            # self.ahosh = None
            # self.isfield = None

    def value(self, fargs, fkwargs, appliable_content):
        value = self.parent.value(fargs, fkwargs, appliable_content) if isinstance(self.parent, AbsAppliable) else self.parent.value
        if isinstance(value, list):
            if len(value) < self.n:  # pragma: no cover
                raise Exception(f"Number of output fields ('{self.n}') should not exceed number of resulting list elements ('{len(value)}').")
            return value[self.index]
        if isinstance(value, dict):
            if len(value) != self.n:  # pragma: no cover
                raise Exception(f"Number of output fields ('{self.n}') should match number of resulting dict entries ('{len(value)}').")
            if self.source:
                return value[self.source]
            return list(sorted(value.items()))[self.index][1]
        else:  # pragma: no cover
            raise Exception(f"Cannot infer subvalue '{self.index}' of type '{type(value)} {value}.")

    def __repr__(self):
        return f"{self.parent}→{str(self.index if self.source is None else self.source)}"
