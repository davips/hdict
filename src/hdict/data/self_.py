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
from hdict.content.argument import AbsBaseArgument

# todo: accept `apply(lambda _: _.x**2)` as shortcut for `apply(lambda d: d.x**2, _)`  ?
class Self_(AbsBaseArgument):
    """
    >>> from hdict import _, apply
    >>> d = _ >> {"x": 5} >> dict(y=7)
    >>> (d >> apply(lambda a: d.x, _).X).evaluated.show(colored=False)
    {
        x: 5,
        y: 7,
        X: 5,
        _id: I.3UGqgTnpbVa5UdEJGdEvGAX53KEr30qdpnfccX,
        _ids: {
            x: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            X: yVmnByh3DGnZwkav2cyJLm24fxJ6x7pjyQFWovy0
        }
    }
    >>> (d >> apply(lambda _: d.x).X).evaluated.show(colored=False)
    {
        x: 5,
        y: 7,
        X: 5,
        _id: nSe4f8qCC8JFPqvV5MnmpmR1UpdXzIwhkta2DNU3,
        _ids: {
            x: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            X: G8MwJEvu5ZxQiWb9U.roscMuvGuPnvSAssWAM4f9
        }
    }
    >>> type(_), type(+_), type(d)
    (<class 'hdict.Self'>, <class 'hdict.Empty'>, <class 'hdict.hdict'>)
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
    >>> str(_ * {})
    '⦑{} » {}⦒'
    """

    def __getattr__(self, item):
        from hdict.content.argument.field import field

        return field(item)

    def __getitem__(self, item):
        from hdict.content.argument.field import field

        return field(item)

    def __call__(self, *args, **kwargs):
        from hdict.content.argument.sample import sample

        return sample(*args)

    def __rshift__(self, other):
        from hdict.data.frozenhdict import frozenhdict

        res = frozenhdict().__rshift__(other)
        if res is NotImplemented:  # pragma: no cover
            return res
        if isinstance(res, frozenhdict):
            res = res.unfrozen
        return res

    def __mul__(self, other):
        from hdict.data.frozenhdict import frozenhdict

        res = frozenhdict().__mul__(other)
        if res is NotImplemented:  # pragma: no cover
            return res
        return res.unfrozen

    def __pos__(self):
        from hdict import Ø

        return Ø
