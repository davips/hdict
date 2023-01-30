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

from shelve import Shelf
from typing import TypeVar

from hdict.cache import cache
from hdict.frozenhdict import frozenhdict
from hosh import Hosh

VT = TypeVar("VT")


class hdict(dict[str, VT]):
    """
    Function id is reversed before application.
    This is needed to enable handling a function as a value, under the original id.

    >>> from hdict import hdict, apply, field
    >>> d = hdict({"x": 3}, y=5)
    >>> d["alpha"] = 11
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        alpha: 11,
        _id: "e6WGyTj7trk6AUUcdxGAefyG.T9j.SvBdEsHF.r5",
        _ids: {
            x: "KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr",
            y: "ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2",
            alpha: "A1RyW.GoA3q9-iCbCvWyWClExm1J3wI.ok6UA3Nk"
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
    >>> d["zz1", "ww1"] = apply(f, field("r1"), y=field("r2"))
    >>> d >>= {("zz2", "ww2"): apply(f, y=field("r2"), x=9)}  # Define external value.
    >>> d >>= {"zzzz": apply(f, y="some str", x=9)}  # Define external 'str' value.
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
    >>> d["zzz1", "www1"] = apply(custom, "str 1", y="str 2")  # Custom callable being applied.
    >>> d["zzz2", "www2"] = apply(field("f"), field("r1"), y="str 2")  # Callable field being applied.
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
        z2: λ(x y)→a,
        w2: λ(x y)→b,
        r1: λ(x),
        r2: λ(x),
        r3: λ(x),
        ra1: λ(x y)→0,
        rb1: λ(x y)→1,
        ra2: λ(x y)→a,
        rb2: λ(x y)→b,
        zz1: λ(r1 r2)→0,
        ww1: λ(r1 r2)→1,
        zz2: λ(9 r2)→0,
        ww2: λ(9 r2)→1,
        zzzz: λ(9 'some s···),
        f: "CustomClass()",
        zzz1: λ('str 1' 'str 2')→0,
        www1: λ('str 1' 'str 2')→1,
        zzz2: λ(r1 'str 2')→0,
        www2: λ(r1 'str 2')→1,
        _id: "4yxiENUUYMLRZWxh.7gN1U2aZcvVM0gkh-rjw4mX",
        _ids: {
            x: "KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr",
            y: "ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2",
            alpha: "A1RyW.GoA3q9-iCbCvWyWClExm1J3wI.ok6UA3Nk",
            beta: "WM5TbiaJ1gLqKRSFiY3VkZEu1PwQcaAokBKBPrWg",
            gamma: "yb-HU.jSxd496XfId1J..MkX7xfUPJOL1-07hHdt",
            p1: "hllpFtAFKUz3OXOJOr3RbpvL8RjwGvwypfgS8WEi",
            q1: "9Fx79MuqFKeorCqJ1Gb-uaGPCwBwT8NliAzSQ2aL",
            pq: "PdulOo9BsqAYMi0.1h15yKZjjq-dExhUHnkJZYO1",
            p2: "LDtY9HmXuNn8uzQyA06-.sb2dMOMSA1H95HZgo2o",
            q2: "VjJ9OEByD74oMAkCXa9QMwyz4HQRWBpGEqhR0l2F",
            z1: "8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt",
            w1: "JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL",
            z2: "8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt",
            w2: "JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL",
            r1: "Y3AxJytRz1Pnf8Q1bjC2jWUs3oTzAALXYkwlH1GI",
            r2: "JdDJ6LPyvJ2xnbPUwBFKDIt8k-udb4czb8PjX8dh",
            r3: "015TXOnn-Z6AfT1ajcNN4brMD6c8YsRn73kA7RPh",
            ra1: "8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt",
            rb1: "JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL",
            ra2: "8dPQ2blIctM6p7mByuoL0EnTlg5no0TxEJtoACbt",
            rb2: "JbWdguqn24m9-XathFYdhhMRBDvWFQVktmxj7gWL",
            zz1: "mQUu0IxSblJEAplB0yVRVN-rY6bv06spvVH8krlt",
            ww1: "7J8PIEG1QPZMBDimMibqHaJPFg6pHG8mQGvDM9Pf",
            zz2: "sHib6xdxGc8tQ6CzacEANreEUZH.sjkZhIa6ZJRc",
            ww2: "FO-4MA-2R.Hp40Fa1cOnY70x.vFfraTBMvYDCTa7",
            zzzz: "eLmNQshNbsczb3UPNUgdswSwjy43T.LaheEWAd9u",
            f: "Some.arbitrary.identifier.with.length.40",
            zzz1: "8psQH6IYL-875mdf0ONueb.GPElYQSs9EVmhUqgk",
            www1: "x.NpepViaL0yjKMHzZbVXeloQksMuGoUQvLZRM2c",
            zzz2: "Hhw3UoRceatED9jYFRkGeUteWupRdQUZab0Vlgud",
            www2: "Ie3whxRJ8TeJurdTfwg7G9zK9CyUfUym.kqsWTgx"
        }
    }
    >>> from hdict import default
    >>> d = hdict(x=2)
    >>> g = lambda x, y: x + y
    >>> d["z"] = apply(f, 2, y=3)
    >>> d["w", "v"] = apply(f, field("x"), y=33)
    >>> d["f"] = f
    >>> d = d >> apply(field("f"), field("x"), y=default(3))("w3", "v3")
    >>> d >>= apply(field("f"), field("x"), y=default(3))("w", "v")
    >>> d["w2", "v2"] = apply(field("f"), field("x"), y=default(3))
    >>> d >>= {"z": apply(f, field("x"), y=3), ("w", "v"): apply(g, y=7)}
    >>> d >>= apply(f, field("x"), y=3)("z9") >> apply(g, y=7)("w9", "v9")
    >>> d >>= apply(f, field("x"), y=3)("z") >> apply(g, y=7)("w", "v")
    >>> from hdict import _
    >>> p = apply(f, y=_[1, 2, 4, ..., 128])("z") >> apply(f, y=_[0, 3, 6, ..., 9])(w="a", v="b")
    >>> from random import Random
    >>> rnd = Random(0)
    >>> p1 = p.sample(rnd)
    >>> d >>= p1

    >>> d["z"] = _(f, 2, y=3)
    >>> d["w", "v"] = _(f, _.x, y=_.x)
    >>> d["w", "v"] = _(_.f, _.x, y=default(3))
    >>> d = hdict() >> {"z": _(f, 7, y=3), ("w", "v"): _(g, default(6), y=7)}
    >>> d = hdict(w=6) >> (_(f, _.w, y=3)("z") >> _(g, x=_[1,2,3,...,5], y=7)("w", "v")).sample()
    >>> p = _(f, y=_[1, 2, 4, ..., 128])("z") >> _(f, y=_[0, 3, 6, ..., 9])(w="a", v="b")
    >>> d = hdict(x=3) >> p.sample(rnd)
    >>> d.show(colored=False)
    {
        x: 3,
        z: λ(x 1)→0,
        w: λ(x 6)→a,
        v: λ(x 6)→b,
        _id: "ViT5bvJGNX4Js4GLFZlCvLfmSP-vMIBCbbG4hMdu",
        _ids: {
            x: "KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr",
            z: "I07Wp60rqEsBRrPZj7sLBGR2mCPxv4u9q4u-2aaw",
            w: "xvV.gAGMoSo-.l1-jk94-GdTaA0qjbgxhxAO3tze",
            v: "NM4FacrCDP3t2ChDaQCNw04xNm1QKwWw4CogLANh"
        }
    }
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary__id: dict | Hosh | str = None, _frozen__cache: frozenhdict | cache = None, **kwargs):
        if isinstance(_dictionary__id, Hosh):
            _dictionary__id = Hosh.id
        if isinstance(_dictionary__id, str):
            # Build hdict from id+cache.
            if len(_dictionary__id) != 40:
                raise Exception(f"id should have lenght of 40, not {len(_dictionary__id)}")
            # TODO: checar for other types like Cache?
            cache_lst = ["<class 'shelchemy.core.Cache'>"]
            if not isinstance(_frozen__cache, (dict, Shelf, list)) and str(_frozen__cache.__class__) not in cache_lst:  # pragma: no cover
                raise Exception("An id argument was provided, but a dict-like cache (or list of caches) is missing as the second argument.")
            if kwargs:  # pragma: no cover
                raise Exception("Cannot pass more arguments when loading from cache (i.e., first argument is an id and the second argument is a dict-like cache).")
            self.frozen = frozenhdict.fromid(_dictionary__id, _frozen__cache)
        else:
            # Build hdict from frozen or fresh data.
            self.frozen = _frozen__cache or frozenhdict(_dictionary__id, **kwargs)

    def __setitem__(self, key: str | tuple, value):
        if isinstance(key, tuple):
            key = tuple((x.start, x.stop) if isinstance(x, slice) else x for x in key)
        self.frozen = self.frozen >> {key: value}

    def __delitem__(self, key):
        data = self.frozen.data.copy()
        del data[key]
        del data["_id"]
        del data["_ids"]
        self.frozen = frozenhdict(data)

    def __getitem__(self, item):
        return self.frozen[item]

    def __getattr__(self, item):
        if item in self.frozen:
            return self.frozen[item]
        return self.__getattribute__(item)

    def __rshift__(self, other):
        from hdict import apply
        from hdict.entry.applyout import applyOut
        from hdict.pipeline import pipeline
        if isinstance(other, apply):
            raise Exception(f"Cannot apply without specifying output.")
        if isinstance(other, (dict, applyOut, pipeline)):
            return (self.frozen >> other).unfrozen
        return NotImplemented

    @property
    def evaluated(self):
        return self.frozen.evaluated

    def evaluate(self):
        """
        >>> from hdict import apply
        >>> d = hdict(x=apply(apply(lambda: 2), {}))
        >>> d.show(colored=False)
        {
            x: λ(),
            _id: "GJC7Qc4lmfpP32nUEG6UAe2fL35KL1wDnubPFgJS",
            _ids: {
                x: "uOjLdXgq4zFpx0Hw7Ofsj1PiXt64oSuLOFpWtD2B"
            }
        }
        >>> d.evaluate()
        >>> d.show(colored=False)
        {
            x: 2,
            _id: "GJC7Qc4lmfpP32nUEG6UAe2fL35KL1wDnubPFgJS",
            _ids: {
                x: "uOjLdXgq4zFpx0Hw7Ofsj1PiXt64oSuLOFpWtD2B"
            }
        }
        >>> d.evaluated.show(colored=False)
        {
            x: 2,
            _id: "GJC7Qc4lmfpP32nUEG6UAe2fL35KL1wDnubPFgJS",
            _ids: {
                x: "uOjLdXgq4zFpx0Hw7Ofsj1PiXt64oSuLOFpWtD2B"
            }
        }
        """
        self.frozen.evaluate()

    @property
    def hosh(self):
        return self.frozen.hosh

    @property
    def id(self):
        """
        >>> from hdict import hdict
        >>> hdict(x=3, y=5).id == hdict(dict(x=3, y=5)).id
        True
        """
        return self.hosh.id

    @property
    def ids(self):
        """
        >>> from hdict import hdict
        >>> hdict(x=3, y=5).ids
        {'x': 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'y': 'ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2'}
        """
        return self.frozen.ids

    @staticmethod
    def fromdict(dictionary, ids):
        """Build an idict from values and pre-defined ids

        >>> from hosh import Hosh
        >>> print(hdict.fromdict({"x": 3, "y": 5, "z": 7}, ids={"x": Hosh(b"x"), "y": Hosh(b"y").id}))
        {x: 3, y: 5, z: 7, _id: "uf--zyyiojm5Tl.vFKALuyGhZRO0e0eH9irosr0i", _ids: {x: "ue7X2I7fd9j0mLl1GjgJ2btdX1QFnb1UAQNUbFGh", y: "5yg5fDxFPxhEqzhoHgXpKyl5f078iBhd.pR0G2X0", z: "eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf"}}
        """
        from hdict.frozenhdict import frozenhdict

        return frozenhdict.fromdict(dictionary, ids).unfrozen

    @property
    def asdict(self):
        """
        >>> from hdict import hdict
        >>> hdict(x=3, y=5).asdict
        {'x': 3, 'y': 5, '_id': 'r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM', '_ids': {'x': 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'y': 'ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2'}}
        """
        return self.frozen.asdict

    @property
    def asdicts(self):
        """
        >>> from hdict import hdict
        >>> hdict(x=3, y=5).asdict
        {'x': 3, 'y': 5, '_id': 'r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM', '_ids': {'x': 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'y': 'ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2'}}
        """
        return self.frozen.asdicts

    def astext(self, colored=True, key_quotes=False):
        r"""
        >>> from hdict import hdict
        >>> repr(hdict(x=3, y=5)) == hdict(x=3, y=5).astext()
        True
        >>> print(repr(hdict(x=3, y=5)))
        {
            x: 3,
            y: 5,
            _id: [38;5;225m[1m[48;5;0mr[0m[38;5;225m[1m[48;5;0m5[0m[38;5;15m[1m[48;5;0mA[0m[38;5;225m[1m[48;5;0m2[0m[38;5;225m[1m[48;5;0mM[0m[38;5;195m[1m[48;5;0mh[0m[38;5;225m[1m[48;5;0m6[0m[38;5;219m[1m[48;5;0mv[0m[38;5;183m[1m[48;5;0mR[0m[38;5;251m[1m[48;5;0mR[0m[38;5;177m[1m[48;5;0mO[0m[38;5;147m[1m[48;5;0m5[0m[38;5;183m[1m[48;5;0mr[0m[38;5;189m[1m[48;5;0mx[0m[38;5;15m[1m[48;5;0mi[0m[38;5;225m[1m[48;5;0m5[0m[38;5;225m[1m[48;5;0mn[0m[38;5;225m[1m[48;5;0mf[0m[38;5;15m[1m[48;5;0mX[0m[38;5;225m[1m[48;5;0mv[0m[38;5;225m[1m[48;5;0m1[0m[38;5;195m[1m[48;5;0mm[0m[38;5;225m[1m[48;5;0my[0m[38;5;219m[1m[48;5;0me[0m[38;5;183m[1m[48;5;0mg[0m[38;5;251m[1m[48;5;0mu[0m[38;5;177m[1m[48;5;0mG[0m[38;5;147m[1m[48;5;0mS[0m[38;5;183m[1m[48;5;0mT[0m[38;5;189m[1m[48;5;0mm[0m[38;5;15m[1m[48;5;0mq[0m[38;5;225m[1m[48;5;0mH[0m[38;5;225m[1m[48;5;0mu[0m[38;5;225m[1m[48;5;0mH[0m[38;5;15m[1m[48;5;0me[0m[38;5;225m[1m[48;5;0mv[0m[38;5;225m[1m[48;5;0m3[0m[38;5;195m[1m[48;5;0m8[0m[38;5;225m[1m[48;5;0mq[0m[38;5;219m[1m[48;5;0mM[0m,
            _ids: {
                x: [38;5;239m[1m[48;5;0mK[0m[38;5;239m[1m[48;5;0mG[0m[38;5;60m[1m[48;5;0mW[0m[38;5;241m[1m[48;5;0mj[0m[38;5;97m[1m[48;5;0mj[0m[38;5;65m[1m[48;5;0m0[0m[38;5;133m[1m[48;5;0mi[0m[38;5;65m[1m[48;5;0my[0m[38;5;97m[1m[48;5;0mL[0m[38;5;66m[1m[48;5;0mA[0m[38;5;132m[1m[48;5;0mn[0m[38;5;61m[1m[48;5;0m1[0m[38;5;66m[1m[48;5;0mR[0m[38;5;95m[1m[48;5;0mG[0m[38;5;95m[1m[48;5;0m6[0m[38;5;239m[1m[48;5;0mR[0m[38;5;239m[1m[48;5;0mT[0m[38;5;239m[1m[48;5;0mG[0m[38;5;60m[1m[48;5;0mt[0m[38;5;241m[1m[48;5;0ms[0m[38;5;97m[1m[48;5;0mG[0m[38;5;65m[1m[48;5;0mE[0m[38;5;133m[1m[48;5;0m3[0m[38;5;65m[1m[48;5;0mo[0m[38;5;97m[1m[48;5;0mm[0m[38;5;66m[1m[48;5;0mZ[0m[38;5;132m[1m[48;5;0mr[0m[38;5;61m[1m[48;5;0ma[0m[38;5;66m[1m[48;5;0mJ[0m[38;5;95m[1m[48;5;0mM[0m[38;5;95m[1m[48;5;0m6[0m[38;5;239m[1m[48;5;0mx[0m[38;5;239m[1m[48;5;0mO[0m[38;5;239m[1m[48;5;0m.[0m[38;5;60m[1m[48;5;0mk[0m[38;5;241m[1m[48;5;0mv[0m[38;5;97m[1m[48;5;0mG[0m[38;5;65m[1m[48;5;0m5[0m[38;5;133m[1m[48;5;0mp[0m[38;5;65m[1m[48;5;0mr[0m,
                y: [38;5;227m[1m[48;5;0me[0m[38;5;221m[1m[48;5;0mc[0m[38;5;209m[1m[48;5;0mv[0m[38;5;149m[1m[48;5;0mg[0m[38;5;221m[1m[48;5;0mo[0m[38;5;215m[1m[48;5;0m-[0m[38;5;185m[1m[48;5;0mC[0m[38;5;221m[1m[48;5;0mB[0m[38;5;216m[1m[48;5;0mP[0m[38;5;192m[1m[48;5;0mi[0m[38;5;227m[1m[48;5;0m7[0m[38;5;222m[1m[48;5;0mw[0m[38;5;191m[1m[48;5;0mR[0m[38;5;215m[1m[48;5;0mW[0m[38;5;180m[1m[48;5;0mI[0m[38;5;192m[1m[48;5;0mx[0m[38;5;227m[1m[48;5;0mN[0m[38;5;221m[1m[48;5;0mz[0m[38;5;209m[1m[48;5;0mu[0m[38;5;149m[1m[48;5;0mo[0m[38;5;221m[1m[48;5;0m1[0m[38;5;215m[1m[48;5;0mH[0m[38;5;185m[1m[48;5;0mg[0m[38;5;221m[1m[48;5;0mH[0m[38;5;216m[1m[48;5;0mQ[0m[38;5;192m[1m[48;5;0mC[0m[38;5;227m[1m[48;5;0mb[0m[38;5;222m[1m[48;5;0md[0m[38;5;191m[1m[48;5;0mv[0m[38;5;215m[1m[48;5;0mR[0m[38;5;180m[1m[48;5;0m0[0m[38;5;192m[1m[48;5;0m5[0m[38;5;227m[1m[48;5;0m8[0m[38;5;221m[1m[48;5;0mx[0m[38;5;209m[1m[48;5;0mi[0m[38;5;149m[1m[48;5;0m6[0m[38;5;221m[1m[48;5;0mz[0m[38;5;215m[1m[48;5;0mm[0m[38;5;185m[1m[48;5;0mr[0m[38;5;221m[1m[48;5;0m2[0m
            }
        }
        """
        return self.frozen.astext(colored, key_quotes)

    def show(self, colored=True, key_quotes=False):
        r"""
        Textual representation of an idict object

        >>> from hdict import hdict
        >>> from hdict.appearance import decolorize
        >>> d = hdict(x=1,y=2)
        >>> d.show(colored=False)
        {
            x: 1,
            y: 2,
            _id: "41wHsGFMSo0vbD2n6zAXogYG9YE3FwzIRSqjWc8N",
            _ids: {
                x: "DYu5bfVvb6FOhBCWNsss4wsEWHZYTbKnsVgoWFvl",
                y: "k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29"
            }
        }
        """
        return self.frozen.show(colored, key_quotes)

    def __iter__(self):
        return iter(self.frozen)

    def __contains__(self, item):
        return item in self.frozen

    def __repr__(self):
        return repr(self.frozen)

    def __str__(self):
        return str(self.frozen)

    def __eq__(self, other):
        return self.frozen == other

    def __ne__(self, other):
        return not (self == other)

    def __reduce__(self):
        return self.frozen.__reduce__()

    def keys(self):
        """Generator of field names, i.e., keys which don't start with '_'"""
        return self.frozen.keys()

    def values(self, evaluate=True):
        """Generator of field values (keys that don't start with '_')"""
        return self.frozen.values(evaluate)

    def items(self, evaluate=True):
        """Generator over field-value pairs

        Exclude ids and other items starting with '_'.

        >>> from hdict import hdict
        >>> from hdict.appearance import decolorize
        >>> for k, v in hdict(x=1, y=2).items():
        ...     print(k, v)
        x 1
        y 2
        """
        return self.frozen.items(evaluate)

    # @property
    # def aslist(self):
    #     return self.frozen.aslist
    #
    # def entries(self, evaluate=True):
    #     """Iterator over all entries
    #
    #     Ignore id entries.
    #
    #     >>> from hdict import hdict
    #     >>> from hdict.appearance import decolorize
    #     >>> for k, v in hdict(x=1, y=2).entries():
    #     ...     print(k, v)
    #     x 1
    #     y 2
    #     """
    #     return self.frozen.entries(evaluate)

    # @property
    # def fields(self):
    #     """
    #     List of keys which don't start with '_'
    #
    #     >>> from hoshmap import idict
    #     >>> idict(x=3, y=5, _z=5).fields
    #     ['x', 'y']
    #     """
    #     return self.frozen.fields

    # @property
    # def metafields(self):
    #     """
    #     List of keys which don't start with '_'
    #
    #     >>> from hoshmap import idict
    #     >>> idict(x=3, y=5, _z=5).metafields
    #     ['_z']
    #     """
    #     return self.frozen.metafields

    # def metakeys(self):
    #     """Generator of keys which start with '_'"""
    #     return self.frozen.metakeys()

    # def metavalues(self, evaluate=True):
    #     """Generator of field values (keys don't start with '_')"""
    #     return self.frozen.metavalues(evaluate)
    #
    # def metaitems(self, evaluate=True):
    #     """Generator over field-entry pairs"""
    #     return self.frozen.metaitems(evaluate)
