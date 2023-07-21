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
from typing import TypeVar

from hdict.content.argument.apply import apply
from hdict.content.argument.field import field
from hdict.content.argument.sample import sample
from hdict.data.empty_ import Empty_
from hdict.content.value import value
from hdict.data.frozenhdict import frozenhdict
from hdict.data.hdict_ import hdict_
from hdict.data.self_ import Self_
from hdict.expression.step.cache import cache

__all__ = ["hdict", "_", "Ø", "apply", "field", "sample", "frozenhdict", "value", "cache"]

VT = TypeVar("VT")


class hdict(hdict_):
    """
    Function id is reversed before application.
    This is needed to enable handling a function as a value, under the original id.

    >>> from hdict import hdict, apply, field
    >>> from hdict.content.argument.default import default
    >>> d = hdict({"x": 3}, y=5)
    >>> d["alpha"] = 11
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        alpha: 11,
        _id: e6WGyTj7trk6AUUcdxGAefyG.T9j.SvBdEsHF.r5,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            alpha: A1RyW.GoA3q9-iCbCvWyWClExm1J3wI.ok6UA3Nk
        }
    }
    >>> d >>= {"beta": 12, "gamma": 17}
    >>> d["p1", "q1"] = apply(lambda x, y=3: [x**y, x/y])
    >>> d["pq"] = apply(lambda x, y=3: [x**y, x/y])
    >>> d["p2", "q2"] = apply(lambda x=2, y=None: [x**y, x/y])
    >>> f = lambda x, y: {"a": x**y, "b": x/y}
    >>> d["z1", "w1"] = apply(f)
    >>> d["z2":"a", "w2":"b"] = apply(f)
    >>> d >>= {
    ...     "r1": apply(lambda x: x**2),
    ...     "r2": apply(lambda x: x**3),
    ...     "r3": apply(lambda x: x**4),
    ...     ("ra1", "rb1"): apply(f),
    ...     (("ra2", "a"), ("rb2", "b")): apply(f),
    ... }
    >>> d["z2"]
    243
    >>> d["zz1", "ww1"] = apply(f, field("r1"), y=field("r2"))
    >>> d >>= {("zz2", "ww2"): apply(f, y=field("r2"), x=9)}  # Define external value.
    >>> d >>= {"zzzz": apply(f, y=13, x=9)}
    >>> # Non-pickable custom classes need a custom 'hosh' attribute to be applied and also to be used as a value.
    >>> from hosh import Hosh
    >>> # Example of class that could be used as a value or as a function.
    >>> from dataclasses import dataclass
    >>> @dataclass
    ... class CustomClass:
    ...     hosh = Hosh.fromid("Some.arbitrary.identifier.with.length.40")
    ...     def __call__(self, x, y):
    ...         return x + y, x / y
    >>> custom = CustomClass()
    >>> d["f"] = custom  # Custom callable handled as a value.
    >>> d["zzz1", "www1"] = apply(custom, 11, y=33)  # Custom callable being applied.
    >>> d["zzz2", "www2"] = apply(field("f"), field("r1"), y=44)  # Callable field being applied.
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        alpha: 11,
        beta: 12,
        gamma: 17,
        p1: λ(x y)→0,
        q1: λ(x y)→1,
        pq: λ(x y),
        p2: λ(x y)→0,
        q2: λ(x y)→1,
        z1: λ(x y)→0,
        w1: λ(x y)→1,
        z2: 243,
        w2: λ(x y)→b,
        r1: λ(x),
        r2: λ(x),
        r3: λ(x),
        ra1: λ(x y)→0,
        rb1: λ(x y)→1,
        ra2: λ(x y)→a,
        rb2: λ(x y)→b,
        zz1: λ(x=r1 y=r2)→0,
        ww1: λ(x=r1 y=r2)→1,
        zz2: λ(9 y=r2)→0,
        ww2: λ(9 y=r2)→1,
        zzzz: λ(9 13),
        f: "CustomClass()",
        zzz1: λ(11 33)→0,
        www1: λ(11 33)→1,
        zzz2: λ(r1 44)→0,
        www2: λ(r1 44)→1,
        _id: i5wtTs5qggivS-y5TNuhnM5jwokjF132M7jF.49a,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            alpha: A1RyW.GoA3q9-iCbCvWyWClExm1J3wI.ok6UA3Nk,
            beta: WM5TbiaJ1gLqKRSFiY3VkZEu1PwQcaAokBKBPrWg,
            gamma: yb-HU.jSxd496XfId1J..MkX7xfUPJOL1-07hHdt,
            p1: Qs0J0I.AhR.brQjpYwUJqDNLk-zKd7FmG0g7gdd1,
            q1: VOAVwyrrdC7eIsjnVkqdpsqUfhprKzKriATFEOQI,
            pq: KtTWRcFQRKVgTJabGMgY-HAQWJ1TZGnOYw7NU.1K,
            p2: qb0H0MqNit0rLwk6CsC4Q2bxpCmBQ581eoGI39sr,
            q2: Sjsl-.MJJ3SK2.INLAJ-0R5BwlfG.tccIpxPFRtB,
            z1: w8obIVknqdoKk.hDUN8TE2M-KiFh-yCCXtxNdrJ4,
            w1: T0hCevYdBG6vWZ3R5Nba.jXacMTFFUW5OjOX4yAO,
            z2: w8obIVknqdoKk.hDUN8TE2M-KiFh-yCCXtxNdrJ4,
            w2: T0hCevYdBG6vWZ3R5Nba.jXacMTFFUW5OjOX4yAO,
            r1: FO3NXIQIi7TBFw1FqLRJYo13EA.uu4Y-L17Fmx0z,
            r2: HorxHsNCdpkm270yeTZ-vREjjFXWIYC99ALidDVU,
            r3: bWc33lXvXHIJXix5Jw2.Nhw0EIsv3TuAa7t8Ix5q,
            ra1: w8obIVknqdoKk.hDUN8TE2M-KiFh-yCCXtxNdrJ4,
            rb1: T0hCevYdBG6vWZ3R5Nba.jXacMTFFUW5OjOX4yAO,
            ra2: w8obIVknqdoKk.hDUN8TE2M-KiFh-yCCXtxNdrJ4,
            rb2: T0hCevYdBG6vWZ3R5Nba.jXacMTFFUW5OjOX4yAO,
            zz1: FB6W9j12qWZ34fUwyrBETzFuAXRB-xn7O1PGhr2j,
            ww1: IhchjkRfjLXpnsC6zl-TFugIQrnUIdB7Wsgpnely,
            zz2: LE5ohPby7q4dNu3qhqgucRcCt.pd87O.CyKWloqe,
            ww2: -RBf-UiccAG3sTH0UFC6C.YFmYcpTRA.0PFP6Oun,
            zzzz: Irbj-xVP8rEIPoylOTNmiuJ-lGdx0dpzIPgq-169,
            f: Some.arbitrary.identifier.with.length.40,
            zzz1: TBw0fUZZo1WlI9uczNuF0w4vC06u6YvzJyNPVEi1,
            www1: WqqXpIpMwinaXxYNqRjj4qttDcKXN.gcGjARpOSh,
            zzz2: .mJim0y-LMUYZi01GN8MTPkHj79JtFdREf7g40ug,
            www2: jwtsaf1IZMG6sWqprXZnc.n-ilyfncwhL3Qr.-Md
        }
    }
    >>> d["p1"]
    243
    >>> from hdict import value
    >>> d.evaluate()
    >>> d = hdict(x=2)
    >>> g = lambda x, y: [x + y, x / y]
    >>> d["z"] = apply(f, 2, y=3)
    >>> d["w", "v"] = apply(f, field("x"), y=33)
    >>> d["f"] = f
    >>> d = d >> apply(field("f"), field("x"), y=default(3), nonexistent_parameter=7)("w3", "v3") # todo: : nonexistent parameter should raise an exception
    >>> d >>= apply(field("f"), field("x"), y=default(3))("w", "v")
    >>> d["w2", "v2"] = apply(field("f"), field("x"), y=default(3))
    >>> d >>= {"z": apply(f, field("x"), y=3), ("w", "v"): apply(g, y=7)}
    >>> d >>= apply(f, field("x"), y=3)("z9") * apply(g, y=7)("w9", "v9")
    >>> pp = apply(f, field("x"), y=3)("z") >> apply(g, y=7)("w", "v")
    >>> d >>= {"x": 3} >> pp >> apply(g, y=7)("w", "v")
    >>> from hdict import _
    >>> a1 = apply(f, y=_(1, 2, 4, ..., 128))
    >>> a2 = apply(f, _(0, 3, 6, ..., 9), y=_(0, 3, 6, ..., 9))
    >>> ppp = hdict() >> a2.sample()("k", "t")
    >>> ppp.show(colored=False)
    {
        k: λ(9 9)→0,
        t: λ(9 9)→1,
        _id: dK-iumb4L5nkFVT9LCkdk3daQtuC.ORk6JwWMhnt,
        _ids: {
            k: rHTgwW.w2SsbcvBlSnWWddLH4vgyXlM1Fhxqr48f,
            t: IldA8m-uSN9lJcE4TBtjTcY-sSiA33mzxQ2k-wpN
        }
    }
    >>> ppp.k
    387420489
    >>> a1("z")
    z=λ(x y=~[1 2 .*. 128])
    >>> a2(w="a", v="b")
    (('w', 'a'), ('v', 'b'))=λ(x=~[0 3 .+. 9] y=~[0 3 .+. 9])
    >>> p = a1("z") >> a2(w="a", v="b")
    >>> h = lambda a, b=4: 5
    >>> app = apply(h, a=_(0, 3, 6, ..., 9))
    >>> app
    λ(a=~[0 3 .+. 9] b=default(4))
    >>> app.c
    c=λ(a=~[0 3 .+. 9] b=default(4))
    >>> sampled = app.sample(0).c
    >>> sampled
    c=λ(9 b=default(4))
    >>> r = hdict() >> sampled
    >>> r.show(colored=False)
    {
        c: λ(9 b=4),
        _id: Bbe5mzn0oCuHZ.Y84-jaEnh3jcrgD8av6IZezKEG,
        _ids: {
            c: 6EehD7OoZe2REI.1YsVLKxSF4hJoYxfOZJLbF.Aj
        }
    }
    >>> r.evaluated.show(colored=False)
    {
        c: 5,
        _id: Bbe5mzn0oCuHZ.Y84-jaEnh3jcrgD8av6IZezKEG,
        _ids: {
            c: 6EehD7OoZe2REI.1YsVLKxSF4hJoYxfOZJLbF.Aj
        }
    }
    >>> from random import Random
    >>> rnd = Random(0)
    >>> p1 = p.sample(rnd)
    >>> d["w"]
    10
    >>> d >>= p1
    >>> d["z"] = apply(f, 2, y=3)
    >>> d["w", "v"] = apply(f, _.x, y=_.x)
    >>> d["w", "v"] = apply(_.f, _.x, y=default(3))
    >>> d = hdict() >> {"z": apply(f, 7, y=3), ("w", "v"): apply(g, default(6), y=7)}
    >>> d = hdict(w=6) >> (apply(f, _["w"], y=3)(z="z") >> apply(g, x=_(1,2,3,...,5), y=7)("ww", "v")).sample(0)
    >>> p = apply(f, y=_(1, 2, 4, ..., 128))("z") >> apply(f, y=_(0, 3, 6, ..., 9))(w="a", v="b")
    >>> d.show(colored=False)
    {
        w: 6,
        z: λ(x=w 3)→z,
        ww: λ(4 7)→0,
        v: λ(4 7)→1,
        _id: x4TxaVuAymsh97Yr.15Oc1ekllvlpECk091124RM,
        _ids: {
            w: CZ7Jm5fQMZ3fZJ3kAVOi0FYK-exFqPqgoYLsGxGl,
            z: No1nN40OXnJ.zOyAvoxwCjyD06cUDiXTZQh4q8xa,
            ww: qZepp.wpXCOYQrwnVIwoZ4kR9pIuMGDQpvRevv80,
            v: wxkjBSP54cKEfxKE1Zte-2dDll3G9Nd-yDh3CLas
        }
    }
    >>> d = hdict(x=3) >> p.sample(rnd)
    >>> d.show(colored=False)
    {
        x: 3,
        z: λ(x 16),
        w: λ(x 9)→a,
        v: λ(x 9)→b,
        _id: 22b-e.CtRGVSoMkektNzHYSVZTouhL2jAHLyPd4Q,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            z: 64cxw0HmJ0fydH7By6i0HrbuwA759XexTu3Bu0Zd,
            w: p1Z5umNo12DHCZtKbh2EClW6TZxv.M447HlALWhv,
            v: HbYbR1RjPdU4jixjW7xSxslRpYx9W6Oiay7maK6F
        }
    }
    >>> d1 = hdict(x=52, y=13)
    >>> d2 = hdict(x=value(52, hosh="1234567890123456789012345678901234567890"))
    >>> d1.show(colored=False)
    {
        x: 52,
        y: 13,
        _id: 5pwGP0LxQRbQaDEk9ztQ4V4qz.A-IIhVNTrcyt8U,
        _ids: {
            x: c.llz05T6ZXw5AlsU4xfmMxcvvHZhLl60LckZis9,
            y: zplslThZYha4haD2VmGxZqrFSw5RJcFJd2E-Ku6s
        }
    }
    >>> d2.show(colored=False)
    {
        x: 52,
        _id: kYzgpPdRgQSYSEpp1qt4EHQLQJXuyb2WDQS-iNPh,
        _ids: {
            x: 1234567890123456789012345678901234567890
        }
    }
    >>> d3 = d1 >> d2
    >>> d3.show(colored=False)
    {
        x: 52,
        y: 13,
        _id: -EFuy5NAeK.LIALpBiZKK-fYQmc9AZYQQck-HiRK,
        _ids: {
            x: 1234567890123456789012345678901234567890,
            y: zplslThZYha4haD2VmGxZqrFSw5RJcFJd2E-Ku6s
        }
    }
    >>> (d3 >> d1.frozen).show(colored=False)
    {
        x: 52,
        y: 13,
        _id: 5pwGP0LxQRbQaDEk9ztQ4V4qz.A-IIhVNTrcyt8U,
        _ids: {
            x: c.llz05T6ZXw5AlsU4xfmMxcvvHZhLl60LckZis9,
            y: zplslThZYha4haD2VmGxZqrFSw5RJcFJd2E-Ku6s
        }
    }

    >>> d = hdict(x=2, y=4)
    >>> {"x": 2, "y": 4} == d.frozen
    True
    >>> {"x": 2, "y": 4} == d
    True
    >>> d == {"x": 2, "y": 4}
    True
    >>> dict(d)
    {'x': 2, 'y': 4}
    >>> hdict() >> {"x": 3} == {"x": 3}
    True
    >>> {"x": 3, "d": {"x": 7}} == hdict(x=3, d=hdict(x=7))
    True
    >>> hdict(x=3, d=hdict(x=7)) == {"x": 3, "d": {"x": 7}}
    True
    >>> {"x": 3, "_id": hdict(x=3).id} == hdict(x=3)
    True
    >>> hdict(x=3) == {"x": 3, "_id": hdict(x=3).id}
    True
    >>> hdict(x=3) == hdict(x=3)
    True
    >>> hdict(x=3).frozen == hdict(x=3)
    True
    >>> hdict(x=3) != {"x": 4}
    True
    >>> hdict(x=3) != hdict(x=4)
    True
    >>> hdict(x=3).frozen != hdict(x=4)
    True
    >>> hdict(x=3) != {"y": 3}
    True
    >>> hdict(x=3) != {"x": 3, "_id": (~hdict(x=3).hosh).id}
    True
    >>> hdict(x=3) != hdict(y=3)
    True
    >>> del d["x"]
    >>> list(d)
    ['y']
    >>> e = d >> apply(lambda y: y*7)("y")
    >>> from hdict.content.aux_value import f2hosh
    >>> print(f2hosh(lambda y: y*7))
    54YCMDJIlsIvMQ.KJtT-vFyjg83Zgfj2xSHOgCj8
    >>> print(e)
    {y: "λ(4)"}
    >>> e.evaluate()
    >>> print(e)
    {y: 28}
    >>> d = d >> apply(lambda y=1: y*7, fhosh="54YCMDJIlsIvMQ.KJtT-vFyjg83Zgfj2xSHOgCj8")("y")
    >>> print(d)
    {y: "λ(4)"}
    >>> d.evaluate()
    >>> print(d)
    {y: 28}
    >>> hash(e.frozen) == hash(d.frozen)
    True
    >>> d = hdict(a=5) >> hdict(y=28)
    >>> d.show(colored=False)
    {
        a: 5,
        y: 28,
        _id: C-xKyWCyBL6g32KIuxoANoF9czLaJTh-emPsMqOg,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9
        }
    }
    >>> d >>= apply(lambda a: a)("x")
    >>> d.show(colored=False)
    {
        a: 5,
        y: 28,
        x: λ(a),
        _id: qI8rmiUzMTSO1pMkCeQJpHTAOw4xuooFqM41iIiY,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9,
            x: sxkIk6E9l8oScCyoGDlzrqJ9QgpIpl5PCBvHlERp
        }
    }
    >>> {"_id": "qI8rmiUzMTSO1pMkCeQJpHTAOw4xuooFqM41iIiY"} == d
    True
    >>> d.show(colored=False)
    {
        a: 5,
        y: 28,
        x: λ(a),
        _id: qI8rmiUzMTSO1pMkCeQJpHTAOw4xuooFqM41iIiY,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9,
            x: sxkIk6E9l8oScCyoGDlzrqJ9QgpIpl5PCBvHlERp
        }
    }
    >>> def f():
    ...     print("busy")
    ...     return 23
    >>> storage = {}
    >>> d >>= apply(f).o >> cache(storage, "x", "y")
    >>> d.y
    28
    >>> d.show(colored=False)
    {
        a: 5,
        y: 28,
        x: ↑↓ cached at `dict`·,
        o: λ(),
        _id: 4FdTqXVIMKldUnZgrrp315c78KHD9yu7T.Nr5zGv,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9,
            x: sxkIk6E9l8oScCyoGDlzrqJ9QgpIpl5PCBvHlERp,
            o: Re1o0YXNebYNezPrVv2dOrFxtgLQutD-b-SHFRbo
        }
    }
    >>> d.evaluated.show(colored=False)
    busy
    {
        a: 5,
        y: 28,
        x: 5,
        o: 23,
        _id: 4FdTqXVIMKldUnZgrrp315c78KHD9yu7T.Nr5zGv,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9,
            x: sxkIk6E9l8oScCyoGDlzrqJ9QgpIpl5PCBvHlERp,
            o: Re1o0YXNebYNezPrVv2dOrFxtgLQutD-b-SHFRbo
        }
    }
    >>> d.evaluated.show(colored=False)
    {
        a: 5,
        y: 28,
        x: 5,
        o: 23,
        _id: 4FdTqXVIMKldUnZgrrp315c78KHD9yu7T.Nr5zGv,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9,
            x: sxkIk6E9l8oScCyoGDlzrqJ9QgpIpl5PCBvHlERp,
            o: Re1o0YXNebYNezPrVv2dOrFxtgLQutD-b-SHFRbo
        }
    }
    """


class Empty(Empty_):
    """
    >>> from hdict import _
    >>> d = _ >> {"x": 5} >> dict(y=7)
    >>> type(+_), type(d)
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
    """


class Self(Self_):
    """"""


Ø = empty = Empty()
_ = Self()
