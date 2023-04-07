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
from hdict.empty_ import Empty_
from hdict.content.value import value
from hdict.frozenhdict import frozenhdict
from hdict.hdict_ import hdict_

__all__ = ["hdict", "_", "Ø", "apply", "field", "sample", "frozenhdict", "value"]

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
        _id: DCHyNhF2j6CaptG.6gb9UL9RVIMztgnnbVI5MHxh,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            alpha: A1RyW.GoA3q9-iCbCvWyWClExm1J3wI.ok6UA3Nk,
            beta: WM5TbiaJ1gLqKRSFiY3VkZEu1PwQcaAokBKBPrWg,
            gamma: yb-HU.jSxd496XfId1J..MkX7xfUPJOL1-07hHdt,
            p1: ggJAsAHfZm2fiI0HmIbBhyZMNP9z06QJEfO24Xx2,
            q1: YMfRygkG8EoBSwIFWwbZfEyHcQ8dlDnKo1.gOijC,
            pq: Zm4nTmd2OIE5Ij9NJjU4DqG.hgqMlJbs1hNjSdRE,
            p2: -RZv1aQW198-uu1wAFsRzS5CalP8THUWSHUgTy6q,
            q2: wPuaLzMJX-wU-b6-z4A7n1hnDi-woaKQq745qo0E,
            z1: 8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt,
            w1: JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL,
            z2: 8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt,
            w2: JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL,
            r1: Y3AxJytRz1Pnf8Q1bjC2jWUs3oTzAALXYkwlH1GI,
            r2: JdDJ6LPyvJ2xnbPUwBFKDIt8k-udb4czb8PjX8dh,
            r3: 015TXOnn-Z6AfT1ajcNN4brMD6c8YsRn73kA7RPh,
            ra1: 8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt,
            rb1: JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL,
            ra2: 8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt,
            rb2: JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL,
            zz1: mQUu0IxSblJEAplB0yVRVN-rY6bv06spvVH8krlt,
            ww1: 7J8PIEG1QPZMBDimMibqHaJPFg6pHG8mQGvDM9Pf,
            zz2: sHib6xdxGc8tQ6CzacEANreEUZH.sjkZhIa6ZJRc,
            ww2: FO-4MA-2R.Hp40Fa1cOnY70x.vFfraTBMvYDCTa7,
            zzzz: GCskxsxNUipp-aSntVX1tASXmXbTqCEJ46YonXVu,
            f: Some.arbitrary.identifier.with.length.40,
            zzz1: Oq-jsn9xtOoG1PvtuUo99Ha-nhgow1Wwbje4TdSd,
            www1: lUCDq9mlpw-qZEx6DRlM5BSq.xj-mOtv.L38Yuti,
            zzz2: ivhVbLM3q-CE9M4.MFf29k3FDj8fU.8GMfZZwKh3,
            www2: fFEl3XJdY9-tX.iVWY2FevFv5SS85e.FDrjZm2NN
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
    >>> cache = {}
    >>> d = d >> apply(field("f"), field("x"), y=default(3), nonexistent_parameter=7)("w3", "v3") # TODO: nonexistent parameter should raise an exception
    >>> d >>= apply(field("f"), field("x"), y=default(3))("w", "v")
    >>> d["w2", "v2"] = apply(field("f"), field("x"), y=default(3))
    >>> d >>= {"z": apply(f, field("x"), y=3), ("w", "v"): apply(g, y=7)}
    >>> d >>= apply(f, field("x"), y=3)("z9") * apply(g, y=7)("w9", "v9")
    >>> pp = apply(f, field("x"), y=3)("z") >> apply(g, y=7)("w", "v")
    >>> type(pp)
    <class 'hdict.expr.Expr'>
    >>> d >>= {"x": 3} >> pp >> apply(g, y=7)("w", "v")
    >>> from hdict import _
    >>> a1 = apply(f, y=_[1, 2, 4, ..., 128])
    >>> a2 = apply(f, _[0, 3, 6, ..., 9], y=_[0, 3, 6, ..., 9])
    >>> ppp = hdict() >> a2.sample()("k", "t")
    >>> ppp.show(colored=False)
    {
        k: λ(9 9)→0,
        t: λ(9 9)→1,
        _id: eeMrAInYUG2lzUrGqgY0vSZd4KpYpc5vu.bV9bbP,
        _ids: {
            k: UgmJcTz6qQgNFiwe.S40EC69Ab6drWQ5JCw8ON3q,
            t: MCyEzFX.viNxTiRwTio0j7dA9LDf-TwFRNKA0JhY
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
    >>> app = apply(h, a=_[0, 3, 6, ..., 9])
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
        _id: -3fKdfaAaTp.4XwUm1FzlzM81PYZSgsIZEuRRCD4,
        _ids: {
            c: Ht.fDdFk9WOHzT27dOKLvaoHY0YB7Nx.Q2MNXTzJ
        }
    }
    >>> r.evaluated.show(colored=False)
    {
        c: 5,
        _id: -3fKdfaAaTp.4XwUm1FzlzM81PYZSgsIZEuRRCD4,
        _ids: {
            c: Ht.fDdFk9WOHzT27dOKLvaoHY0YB7Nx.Q2MNXTzJ
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
    >>> d = hdict(w=6) >> (apply(f, _.w, y=3)(z="z") >> apply(g, x=_[1,2,3,...,5], y=7)("ww", "v")).sample(0)
    >>> p = apply(f, y=_[1, 2, 4, ..., 128])("z") >> apply(f, y=_[0, 3, 6, ..., 9])(w="a", v="b")
    >>> d.show(colored=False)
    {
        w: 6,
        z: λ(x=w 3)→z,
        ww: λ(4 7)→0,
        v: λ(4 7)→1,
        _id: Hu.P9nMRy97xUe7prRc3k-Uwvz2p5emCpSyVSdIC,
        _ids: {
            w: CZ7Jm5fQMZ3fZJ3kAVOi0FYK-exFqPqgoYLsGxGl,
            z: 3eItvrVzHQPDEYbQRbksBHiCaQbe2Ia2m7Z2P1lw,
            ww: VdHav0HHdJC6gfOF8Fqw7AFX9IYQyrIUOZc8G.Pp,
            v: KtYqDG5UPyrYEv-5V5RaUQasieAwAjF1bYf3Tvyy
        }
    }
    >>> d = hdict(x=3) >> p.sample(rnd)
    >>> d.show(colored=False)
    {
        x: 3,
        z: λ(x 16),
        w: λ(x 9)→a,
        v: λ(x 9)→b,
        _id: OIVFm0IdYK3jtOApTVCwdLTVXXNGarxDkUCwB0Iv,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            z: -F83hM-wE8ykmcEM1XvuG.XBpo7rzkuHfNKzTVMz,
            w: G7CpHeVpUD5KfNpJmRaMC2Rt4rTeQjIuAeGuZXSa,
            v: glVBFsjtDi7RrpvqrV.5vh.dp.RgASp25V-qlClj
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
    >>> from hdict.hoshfication import f2hosh
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
        _id: q5J7ZUr3gs0bKrG4AxVEY2q0-XH3Suvw5X8-j6do,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9,
            x: gak9o6ZS9plw9l63f0WtAFnr52.1HycGhc3En2MR
        }
    }
    >>> {"_id": "q5J7ZUr3gs0bKrG4AxVEY2q0-XH3Suvw5X8-j6do"} == d
    True
    >>> d.show(colored=False)
    {
        a: 5,
        y: 28,
        x: λ(a),
        _id: q5J7ZUr3gs0bKrG4AxVEY2q0-XH3Suvw5X8-j6do,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            y: -2A0hTRBN1wtIKQxLzRcYDBkhv1hu-dMY-24Jye9,
            x: gak9o6ZS9plw9l63f0WtAFnr52.1HycGhc3En2MR
        }
    }
    """


class Empty(Empty_):
    """
    >>> from hdict import _
    >>> d = _ >> {"x": 5} >> dict(y=7)
    >>> type(_), type(d)
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


Ø = _ = Empty()
