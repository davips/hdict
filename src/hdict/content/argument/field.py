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

from hdict.content.argument import AbsBaseArgument


@dataclass
class field(AbsBaseArgument):
    """
    Pointer to a field, without knowing the concrete value yet

    >>> from hdict import Ø, _, apply
    >>> d = Ø
    >>> d.show(colored=False)
    {
        _id: 0000000000000000000000000000000000000000,
        _ids: {}
    }
    >>> d = +_
    >>> d.show(colored=False)
    {
        _id: 0000000000000000000000000000000000000000,
        _ids: {}
    }
    >>> d >>= {"x": 3, "y": 5} >> apply(lambda x, y: x + y).z
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        z: λ(x y),
        _id: ..SSoOQF.FYZDUevP1CGj0DJVc.M8cgimN70yI3C,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: 3j029VhuvENAnBK6JLRGl8ePpsQybm57sXKfX2oo
        }
    }
    >>> d >>= {"x": 3, "y": 5} >> apply(lambda x, y: x + y).x
    >>> d.x
    8
    >>> d["x"] = apply(lambda x, y: x + y)
    >>> d.x
    13
    """

    name: str

    def __repr__(self):
        return f"field({self.name})"
