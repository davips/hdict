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

from hdict.data.frozenhdict import frozenhdict


class Empty_(frozenhdict):
    """
    >>> from hdict import Ø
    >>> d = Ø >> {"x": 5} >> dict(y=7)
    >>> type(Ø), type(d)
    (<class 'hdict.Empty'>, <class 'hdict.hdict'>)
    >>> d.show(colored=False)
    {
        x: 5,
        y: 7,
        _id: A0G3Y7KNMLihDvpSJ3tB.zxshc6u1CbbiiYjCAAA,
        _ids: {
            x: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf
        }
    }
    >>> str(Ø * {})
    '⦑{} » {}⦒'
    """

    def __rshift__(self, other):
        res = super().__rshift__(other)
        if res is NotImplemented:  # pragma: no cover
            return res
        if isinstance(res, frozenhdict):
            res = res.unfrozen
        return res

    def __mul__(self, other):
        res = super().__mul__(other)
        if res is NotImplemented:  # pragma: no cover
            return res
        return res.unfrozen
