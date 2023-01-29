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

from hdict.entry.abscontent import AbsContent
from hdict.hoshfication import v2hosh
from hosh import Hosh


class value(AbsContent):
    """
    >>> x = 5
    >>> from hdict.entry.value import value
    >>> v = value(x, "1234567890123456789012345678901234567890")
    >>> v
    5
    >>> v.hosh.id
    '1234567890123456789012345678901234567890'

    """

    def __init__(self, value: object, hosh: Hosh | str = None, hdict=None):
        """

        Args:
            value:
            hosh:
            hdict:  optional reference to the object if it has a hdict counterpart (e.g.: pandas DF)
        """
        if isinstance(value, AbsContent):
            raise Exception(f"Cannot nest AbsContent object inside a 'value' object: '{type(value)}")
        self.value = value
        if isinstance(hosh, str):
            hosh = Hosh.fromid(hosh)
        self.hosh = v2hosh(self.value) if hosh is None else hosh
        self.hdict = hdict
        self.isevaluated = True

    def __repr__(self):
        return repr(self.value)

#  d["z"] = apply(f, 2, y=3)
#  d["w", "v"] = apply(f, field("x"), y=field("y"))
#  d["w", "v"] = apply(field("f"), field("x"), y=default(3))
#  d = hdict() >> {"z": apply(f, field("x"), y=3), ("w", "v"): apply(g, y=7)}
#  d = hdict() >> apply(f, field("x"), y=3)("z") >> apply(g, y=7)("w", "v")
#  p = apply(f, y=_[1, 2, 4, ..., 128])("z") * apply(f, y=_[0, 3, 6, ..., 9])(w="a", v="b")
#  d = p.sample(rnd)

#  d["z"] = _(f, 2, y=3)
#  d["w", "v"] = _(f, _.x, y=_.y)
#  d["w", "v"] = _(_.f, _.x), y=default(3))
#  d = hdict() >> {"z": _(f, _.x, y=3), ("w", "v"): _(g, y=7)}
#  d = hdict() >> _(f, _.x, y=3)("z") >> _(g, y=7)("w", "v")
#  p = _(f, y=_[1, 2, 4, ..., 128])("z") * _(f, y=_[0, 3, 6, ..., 9])(w="a", v="b")
#  d = p.sample(rnd)
