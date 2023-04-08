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
from typing import TypeVar, Union

from hdict.frozenhdict import frozenhdict

VT = TypeVar("VT")


# TODO: finish all '*' combinations and check all '>>' to see when to generate hdict and when to generate Expr.


class hdict_(dict[str, VT]):
    """
    This class was created only due to slowness of IDE created by excessive doctests in the main file.
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary: dict = None, _frozen: frozenhdict = None, **kwargs):
        # Build hdict from frozen or fresh data. Never both.
        self.frozen = _frozen or frozenhdict(_dictionary, **kwargs)

    def __setitem__(self, key: str | tuple, value):
        if isinstance(key, tuple):
            key = tuple((x.start, x.stop) if isinstance(x, slice) else x for x in key)
        self.frozen = self.frozen >> {key: value}

    def __delitem__(self, key):
        data = self.frozen.data.copy()
        del data[key]
        self.frozen = frozenhdict(data)

    def __getitem__(self, item):
        return self.frozen[item]

    def __getattr__(self, item):
        if item in self.frozen:
            return self.frozen[item]
        return self.__getattribute__(item)  # pragma: no cover

    def __rrshift__(self, other):
        return (other >> self.frozen).unfrozen

    def __rshift__(self, other):
        from hdict.content.argument import AbsArgument
        from hdict.applyout import ApplyOut

        if isinstance(other, AbsArgument):  # pragma: no cover
            raise Exception(f"Cannot pipe {type(other).__name__} without specifying output.\n" "Hint: d >> {'field name': object}")
        # REMINDER: dict includes hdict/frozenhdict.
        if isinstance(other, (dict, ApplyOut)):
            return (self.frozen >> other).unfrozen
        return NotImplemented  # pragma: no cover

    @property
    def evaluated(self):
        return self.frozen.evaluated

    def evaluate(self):
        """
        >>> from hdict import apply, hdict
        >>> d = hdict(x=apply(apply(lambda: 2)))
        >>> d.show(colored=False)
        {
            x: λ(),
            _id: GJC7Qc4lmfpP32nUEG6UAe2fL35KL1wDnubPFgJS,
            _ids: {
                x: uOjLdXgq4zFpx0Hw7Ofsj1PiXt64oSuLOFpWtD2B
            }
        }
        >>> d.evaluate()
        >>> d.show(colored=False)
        {
            x: 2,
            _id: GJC7Qc4lmfpP32nUEG6UAe2fL35KL1wDnubPFgJS,
            _ids: {
                x: uOjLdXgq4zFpx0Hw7Ofsj1PiXt64oSuLOFpWtD2B
            }
        }
        >>> d.evaluated.show(colored=False)
        {
            x: 2,
            _id: GJC7Qc4lmfpP32nUEG6UAe2fL35KL1wDnubPFgJS,
            _ids: {
                x: uOjLdXgq4zFpx0Hw7Ofsj1PiXt64oSuLOFpWtD2B
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
        >>> from hdict import hdict
        >>> e = hdict.fromdict({"x": 3, "y": 5, "z": 7}, ids={"x": Hosh(b"x"), "y": Hosh(b"y").id})
        >>> e.show(colored=False)
        {
            x: 3,
            y: 5,
            z: 7,
            _id: uf--zyyiojm5Tl.vFKALuyGhZRO0e0eH9irosr0i,
            _ids: {
                x: ue7X2I7fd9j0mLl1GjgJ2btdX1QFnb1UAQNUbFGh,
                y: 5yg5fDxFPxhEqzhoHgXpKyl5f078iBhd.pR0G2X0,
                z: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf
            }
        }
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

    @property
    def asdicts_noid(self):
        return self.frozen.asdicts_noid

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
        >>> d = hdict(x=1,y=2)
        >>> d.show(colored=False)
        {
            x: 1,
            y: 2,
            _id: 41wHsGFMSo0vbD2n6zAXogYG9YE3FwzIRSqjWc8N,
            _ids: {
                x: DYu5bfVvb6FOhBCWNsss4wsEWHZYTbKnsVgoWFvl,
                y: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29
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
        return self.frozen != other

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
        >>> for k, v in hdict(x=1, y=2).items():
        ...     print(k, v)
        x 1
        y 2
        """
        return self.frozen.items(evaluate)

    def __hash__(self):  # pragma: no cover
        raise Exception(f"hdict is not hashable. Please use hdict.frozen instead.")

    def save(self, cache: dict):
        """
        Store an entire hdict

        >>> from hdict import hdict, apply
        >>> cache = {}
        >>> d = hdict(x=3, y=7, z=hdict(z=9)) >> apply(lambda x, y: x/y).w
        >>> d.show(colored=False)
        {
            x: 3,
            y: 7,
            z: {
                z: 9,
                _id: izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM,
                _ids: {
                    z: GuwIQCrendfKXZr5jGfrUwoP-8TWMhmLHYrja2yj
                }
            },
            w: λ(x y),
            _id: s3aPQRspwLR81It8zlXsD3Da1Gg76DGSDe841d0b,
            _ids: {
                x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
                y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
                z: izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM,
                w: vo3qMHk3Ef-O065cO-sb4MLHq69x6bKSU694sREJ
            }
        }
        >>> d.save(cache)
        >>> cache
        {'izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM': {'z': 'GuwIQCrendfKXZr5jGfrUwoP-8TWMhmLHYrja2yj'}, 'GuwIQCrendfKXZr5jGfrUwoP-8TWMhmLHYrja2yj': 9, 's3aPQRspwLR81It8zlXsD3Da1Gg76DGSDe841d0b': {'x': 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'y': 'eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf', 'z': 'izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM', 'w': 'vo3qMHk3Ef-O065cO-sb4MLHq69x6bKSU694sREJ'}, 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr': 3, 'eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf': 7, 'vo3qMHk3Ef-O065cO-sb4MLHq69x6bKSU694sREJ': 0.42857142857142855}
        >>> e = hdict.load(d.id, cache)
        >>> e.show(colored=False)
        {
            x: «lazy value at cache `dict`»,
            y: «lazy value at cache `dict`»,
            z: «lazy value at cache `dict`»,
            w: «lazy value at cache `dict`»,
            _id: s3aPQRspwLR81It8zlXsD3Da1Gg76DGSDe841d0b,
            _ids: {
                x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
                y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
                z: izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM,
                w: vo3qMHk3Ef-O065cO-sb4MLHq69x6bKSU694sREJ
            }
        }
        >>> d.w
        0.42857142857142855
        >>> e.w
        0.42857142857142855
        >>> e.evaluate()
        >>> e.show(colored=False)
        {
            x: 3,
            y: 7,
            z: {
                z: "GuwIQCrendfKXZr5jGfrUwoP-8TWMhmLHYrja2yj"
            },
            w: 0.42857142857142855,
            _id: s3aPQRspwLR81It8zlXsD3Da1Gg76DGSDe841d0b,
            _ids: {
                x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
                y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
                z: izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM,
                w: vo3qMHk3Ef-O065cO-sb4MLHq69x6bKSU694sREJ
            }
        }
        """
        self.frozen.save(cache)

    @staticmethod
    def fetch(id, cache, lazy=True, ishdict=False) -> Union["frozenhdict", None]:
        """
        Fetch a single entry

        When cache is a list, traverse it from the end (right item to the left item).
        """
        return frozenhdict.fetch(id, cache, lazy, ishdict).unfrozen

    @staticmethod
    def load(id, cache):
        """
        Fetch an entire hdict

        >>> from hdict import _
        >>> fid = "1234567890123456789012345678901234567890"
        >>> did = "0000567890123456789012345678901234567890"
        >>> cache = {did: {"x": fid}, fid: 5}
        >>> d = _.load(did, cache)
        >>> d.show(colored=False)
        {
            x: «lazy value at cache `dict`»,
            _id: kYzgpPdRgQSYSEpp1qt4EHQLQJXuyb2WDQS-iNPh,
            _ids: {
                x: 1234567890123456789012345678901234567890
            }
        }
        >>> d.evaluate()
        >>> d.show(colored=False)
        {
            x: 5,
            _id: kYzgpPdRgQSYSEpp1qt4EHQLQJXuyb2WDQS-iNPh,
            _ids: {
                x: 1234567890123456789012345678901234567890
            }
        }
        """
        return frozenhdict.load(id, cache).unfrozen

    @staticmethod
    def fromfile(name, fields=None, format="df", include_name=False):
        """Input format is defined by file extension: .arff, .csv"""
        from hdict.data.load import file2df
        from hdict.data.dataset import df2Xy

        if fields is None:
            fields = ["df"]
        df, name = file2df(name)
        # if include_name
        if format == "df":
            if fields == ["X", "y"]:
                fields = ["df"]
            if len(fields) != 1:  # pragma: no cover
                raise Exception(f"Wrong number of fields {len(fields)}. Expected: 1.", fields)
            return frozenhdict({fields[0]: df})
        elif format == "Xy":
            if fields == ["df"]:
                fields = ["X", "y"]
            if len(fields) != 2:  # pragma: no cover
                raise Exception(f"Wrong number of fields {len(fields)}. Expected: 2.", fields)
            dic = df2Xy(df=df)
            del dic["_history"]
            return frozenhdict({fields[0]: dic["X"], fields[1]: dic["y"]})
        else:  # pragma: no cover
            raise Exception(f"Unknown {format=}.")

    # def __reduce__(self):
    #     return self.frozen.__reduce__()

    def __mul__(self, other):
        from hdict.expr import Expr

        return Expr(self, other)
