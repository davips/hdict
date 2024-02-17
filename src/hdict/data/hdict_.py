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

from hosh import Hosh

from hdict.content.argument.apply import apply
from hdict.content.argument.field import field
from hdict.data.frozenhdict import frozenhdict

VT = TypeVar("VT")


# todo: : finish all '*' combinations and check all '>>' to see when to generate hdict and when to generate Expr.

# todo: incluir no pacote esquema de aplicar f no hdict inteiro como feito no artigo.
#  seria outro hdict ou só precisaria de uma função wrapper para f? ou um h_apply que transforma o hdict inteiro?


class hdict_(dict[str, VT]):
    """
    This class was created only due to slowness of IDE created by excessive doctests in the main file.

    >>> from hdict import _, apply
    >>> e = hdict_() * dict() * hdict_()
    >>> e.show(colored=False)
    ⦑{
        _id: 0000000000000000000000000000000000000000,
        _ids: {}
    } » {} » {}⦒
    >>> d = {"x": 3, "f": lambda x: x+1} >> e >> apply(_.f, _.x).x
    >>> bool(d), bool(e.sample())
    (True, False)
    >>> d.show(colored=False)  # doctest:+ELLIPSIS
    {
        x: λ(3),
        f: "<function <lambda> at 0x...>",
        _id: KxAogdPlPbTXATJzW7E8C.4j.82ZIDrVpTbVRxiZ,
        _ids: {
            x: KeU-dCTjUgnSYGRNrrMMr4i.hg64Dkkfb3c14eh3,
            f: p-nM7oHlOFr6iHSF9ZISWXc9zqi017c3zcvcV8Dr
        }
    }
    >>> d.x
    4
    >>> d.show(colored=False)  # doctest:+ELLIPSIS
    {
        x: 4,
        f: "<function <lambda> at 0x...>",
        _id: KxAogdPlPbTXATJzW7E8C.4j.82ZIDrVpTbVRxiZ,
        _ids: {
            x: KeU-dCTjUgnSYGRNrrMMr4i.hg64Dkkfb3c14eh3,
            f: p-nM7oHlOFr6iHSF9ZISWXc9zqi017c3zcvcV8Dr
        }
    }
    >>> str({"a": 2} * d)  # doctest:+ELLIPSIS
    '⦑{a: 2} » {x: 4, f: "<function <lambda> at 0x...>"}⦒'
    >>> (d >> apply(lambda d: d.x, _).X).evaluated.show(colored=False)  # doctest:+ELLIPSIS
    {
        x: 4,
        f: "<function <lambda> at 0x...>",
        X: 4,
        _id: KaIR9dqecR44MZVRrXLUzwqnIbCHhbOkQswgCuQl,
        _ids: {
            x: KeU-dCTjUgnSYGRNrrMMr4i.hg64Dkkfb3c14eh3,
            f: p-nM7oHlOFr6iHSF9ZISWXc9zqi017c3zcvcV8Dr,
            X: M411IcX.kF9pEdsWGIiS-XGn.R45qYTVQS0ewQs2
        }
    }
    >>> (d >> apply(lambda _: _.x).X).evaluated.show(colored=False)  # doctest:+ELLIPSIS
    {
        x: 4,
        f: "<function <lambda> at 0x...>",
        X: 4,
        _id: c1ZgriP45q8xEmDTkRcHjYe2v1C7RLyyZK4NgQ0L,
        _ids: {
            x: KeU-dCTjUgnSYGRNrrMMr4i.hg64Dkkfb3c14eh3,
            f: p-nM7oHlOFr6iHSF9ZISWXc9zqi017c3zcvcV8Dr,
            X: nVVYNVw8RyQ-7Kv0CxAUeLjRIzZwZwE7-8BKaaFr
        }
    }
    >>> (d >> apply(lambda _: _["x"] * 3).s).evaluated.show(colored=False)  # doctest:+ELLIPSIS
    {
        x: 4,
        f: "<function <lambda> at 0x...>",
        s: 12,
        _id: iht2boR5MlpURpv7HldOcsWeXaV.4LF80tBnMQ49,
        _ids: {
            x: KeU-dCTjUgnSYGRNrrMMr4i.hg64Dkkfb3c14eh3,
            f: p-nM7oHlOFr6iHSF9ZISWXc9zqi017c3zcvcV8Dr,
            s: Dhu.akwH18RjAvlq9DktCNMfVu5zH.segcKI6AZ0
        }
    }
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary: dict = None, _frozen: frozenhdict = None, **kwargs):
        # Build hdict from frozen or fresh data. Never both.
        self.frozen = _frozen or frozenhdict(_dictionary, **kwargs)
        self.raw = self.frozen.data

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

    def __rmul__(self, other):
        return other * self.frozen

    def __mul__(self, other):
        return self.frozen * other

    def __rrshift__(self, other):
        return (other >> self.frozen).unfrozen

    def __rshift__(self, other):
        return (self.frozen >> other).unfrozen

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
            _id: YwRX7paX43aafhz-Jndo9HYnvyMSOtPEbRDjgQ3r,
            _ids: {
                x: J746LLRT3gd5glC2ZiaHBgHegmewpiOMC4Sq4bp9
            }
        }
        >>> d.evaluate()
        >>> d.show(colored=False)
        {
            x: 2,
            _id: YwRX7paX43aafhz-Jndo9HYnvyMSOtPEbRDjgQ3r,
            _ids: {
                x: J746LLRT3gd5glC2ZiaHBgHegmewpiOMC4Sq4bp9
            }
        }
        >>> d.evaluated.show(colored=False)
        {
            x: 2,
            _id: YwRX7paX43aafhz-Jndo9HYnvyMSOtPEbRDjgQ3r,
            _ids: {
                x: J746LLRT3gd5glC2ZiaHBgHegmewpiOMC4Sq4bp9
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
        from hdict.data.frozenhdict import frozenhdict

        return frozenhdict.fromdict(dictionary, ids).unfrozen

    @property
    def asdict(self):
        """
        Convert to 'dict', including ids.

        This evaluates all fields.
        HINT: Use 'dict(d)' to convert 'hdict' to 'dict' excluding ids.

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

    def save(self, storage: dict):
        """
        Store an entire hdict

        >>> from hdict import hdict, apply
        >>> storage = {}
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
            _id: Jf8QtLAszezNdiqblJCXMuoXocCWZ90QwrxY90Zu,
            _ids: {
                x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
                y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
                z: izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM,
                w: NjWbIhEnN3s8E-w61pptxBuiYmqQ2D3QNX2ZAEB1
            }
        }
        >>> d.save(storage)
        >>> storage
        {'izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM': {'z': 'GuwIQCrendfKXZr5jGfrUwoP-8TWMhmLHYrja2yj'}, 'GuwIQCrendfKXZr5jGfrUwoP-8TWMhmLHYrja2yj': Stored(content=9), 'Jf8QtLAszezNdiqblJCXMuoXocCWZ90QwrxY90Zu': {'x': 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'y': 'eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf', 'z': 'izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM', 'w': 'NjWbIhEnN3s8E-w61pptxBuiYmqQ2D3QNX2ZAEB1'}, 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr': Stored(content=3), 'eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf': Stored(content=7), 'NjWbIhEnN3s8E-w61pptxBuiYmqQ2D3QNX2ZAEB1': Stored(content=0.42857142857142855)}
        >>> e = hdict.load(d.id, storage)
        >>> e.show(colored=False)
        {
            x: ↑↓ cached at `dict`·,
            y: ↑↓ cached at `dict`·,
            z: ↑↓ cached at `dict`·,
            w: ↑↓ cached at `dict`·,
            _id: Jf8QtLAszezNdiqblJCXMuoXocCWZ90QwrxY90Zu,
            _ids: {
                x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
                y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
                z: izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM,
                w: NjWbIhEnN3s8E-w61pptxBuiYmqQ2D3QNX2ZAEB1
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
                z: 9
            },
            w: 0.42857142857142855,
            _id: Jf8QtLAszezNdiqblJCXMuoXocCWZ90QwrxY90Zu,
            _ids: {
                x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
                y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
                z: izn67XbX0tQNF6E5qkwniN2jxZg5MT6f7z5AJzPM,
                w: NjWbIhEnN3s8E-w61pptxBuiYmqQ2D3QNX2ZAEB1
            }
        }
        """
        self.frozen.save(storage)

    @staticmethod
    def fetch(id: str, storage: dict, lazy=True) -> Union["hdict_", None]:
        r"""
        Fetch a single entry

        When cache is a list, traverse it from the end (right item to the left item).

        >>> from hdict import hdict, cache
        >>> from testfixtures import TempDirectory
        >>> arff = "@RELATION mini\n@ATTRIBUTE attr1	REAL\n@ATTRIBUTE attr2 	REAL\n@ATTRIBUTE class 	{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1"
        >>> with TempDirectory() as tmp:  # doctest:+ELLIPSIS
        ...    tmp.write("mini.arff", arff.encode())
        ...    d = hdict.fromfile(tmp.path + "/mini.arff", fields=["df"])
        ...    d2 = hdict.fromfile(tmp.path + "/mini.arff", fields=["df"], named=True)
        '/tmp/.../mini.arff'
        >>> d.show(colored=False)
        {
            df: "‹{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}, 'class': {0: '0', 1: '1'}}›",
            _id: YaEOJ7a7aOUux8qb1lY3mucUo6AU4vVv15JhAnn2,
            _ids: {
                df: Sxa-cdrwGU60j--6mK9FvWc7IaYdeYB-2yzSi62B
            }
        }
        >>> d2.show(colored=False)
        {
            df: "‹{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}, 'class': {0: '0', 1: '1'}}›",
            name: " mini",
            _id: NuQ3MtEDc-RqAgxUtgEJdg1wnQngv2koODT8GrqU,
            _ids: {
                df: Sxa-cdrwGU60j--6mK9FvWc7IaYdeYB-2yzSi62B,
                name: 5nzeWHgeVef.PD8CnIrPcjwGqaYoRCXK0iwH0cKm
            }
        }
        >>> storage = {}
        >>> d.save(storage)
        >>> d = hdict.fetch(d.id, storage)
        >>> d.show(colored=False)
        {
            df: ↑↓ cached at `dict`·,
            _id: YaEOJ7a7aOUux8qb1lY3mucUo6AU4vVv15JhAnn2,
            _ids: {
                df: Sxa-cdrwGU60j--6mK9FvWc7IaYdeYB-2yzSi62B
            }
        }
        >>> d.df
           attr1  attr2 class
        0    5.1    3.5     0
        1    3.1    4.5     1

        # >>> #d.df.show(colored=False)
        # >>> d = hdict.fetch(d.id, storage, lazy=False)
        # >>> d.show(colored=False)
        # {
        #     df: {
        #         index: "‹{0: 0, 1: 1}›",
        #         "attr1@REAL": "‹{0: 5.1, 1: 3.1}›",
        #         "attr2@REAL": "‹{0: 3.5, 1: 4.5}›",
        #         "class@{0,1}": "‹{0: '0', 1: '1'}›",
        #         _id: cHrG-npBDd2VEB8Foeg.7jQNZtdkTM1uhouHgW.J,
        #         _ids: {
        #             index: DQa5yWRkGo-9FLqmaST8pbElYdUEgqF8xPvip6-3,
        #             "attr1@REAL": wsy0JDrZO04O0RVwr64jpawX62WmCKtddYdvZlwm,
        #             "attr2@REAL": LvEgUazJoB1-.A3kABbskN-.iauWmWLTTo1iC51n,
        #             "class@{0,1}": b.kJy3SrU-JQ1oeh1d.uWLO7Pqh-eW6zwK78nTY4
        #         }
        #     },
        #     df_: λ({    i···),
        #     _id: CWkreYbSmrL0DPN9OtoU4Za1dg8.Jjl.fXD6yblb,
        #     _ids: {
        #         df: cHrG-npBDd2VEB8Foeg.7jQNZtdkTM1uhouHgW.J,
        #         df_: cHrG-npBDd2VEB8Foeg.7jQNZtdkTM1uhouHgW.J
        #     }
        # }
        # >>> #del d["df_"]
        # >>> d.show(colored=False)
        # {
        #     df: {
        #         index: "‹{0: 0, 1: 1}›",
        #         "attr1@REAL": "‹{0: 5.1, 1: 3.1}›",
        #         "attr2@REAL": "‹{0: 3.5, 1: 4.5}›",
        #         "class@{0,1}": "‹{0: '0', 1: '1'}›",
        #         _id: cHrG-npBDd2VEB8Foeg.7jQNZtdkTM1uhouHgW.J,
        #         _ids: {
        #             index: DQa5yWRkGo-9FLqmaST8pbElYdUEgqF8xPvip6-3,
        #             "attr1@REAL": wsy0JDrZO04O0RVwr64jpawX62WmCKtddYdvZlwm,
        #             "attr2@REAL": LvEgUazJoB1-.A3kABbskN-.iauWmWLTTo1iC51n,
        #             "class@{0,1}": b.kJy3SrU-JQ1oeh1d.uWLO7Pqh-eW6zwK78nTY4
        #         }
        #     },
        #     _id: CWkreYbSmrL0DPN9OtoU4Za1dg8.Jjl.fXD6yblb,
        #     _ids: {
        #         df: cHrG-npBDd2VEB8Foeg.7jQNZtdkTM1uhouHgW.J
        #     }
        # }
        # >>> d.save(storage)
        # >>> d = hdict.fetch(d.id, storage, lazy=False)
        # >>> d.show(colored=False)
        # {
        #     df: {
        #         index: "‹{0: 0, 1: 1}›",
        #         "attr1@REAL": "‹{0: 5.1, 1: 3.1}›",
        #         "attr2@REAL": "‹{0: 3.5, 1: 4.5}›",
        #         "class@{0,1}": "‹{0: '0', 1: '1'}›",
        #         _id: cHrG-npBDd2VEB8Foeg.7jQNZtdkTM1uhouHgW.J,
        #         _ids: {
        #             index: DQa5yWRkGo-9FLqmaST8pbElYdUEgqF8xPvip6-3,
        #             "attr1@REAL": wsy0JDrZO04O0RVwr64jpawX62WmCKtddYdvZlwm,
        #             "attr2@REAL": LvEgUazJoB1-.A3kABbskN-.iauWmWLTTo1iC51n,
        #             "class@{0,1}": b.kJy3SrU-JQ1oeh1d.uWLO7Pqh-eW6zwK78nTY4
        #         }
        #     },
        #     _id: CWkreYbSmrL0DPN9OtoU4Za1dg8.Jjl.fXD6yblb,
        #     _ids: {
        #         df: cHrG-npBDd2VEB8Foeg.7jQNZtdkTM1uhouHgW.J
        #     }
        # }
        # >>> str(d)
        # '{df: {index: "‹{0: 0, 1: 1}›", attr1@REAL: "‹{0: 5.1, 1: 3.1}›", attr2@REAL: "‹{0: 3.5, 1: 4.5}›", class@{0,1}: "‹{0: \'0\', 1: \'1\'}›"}}'
        """
        return frozenhdict.fetch(id, storage, lazy, ishdict=False)

    @staticmethod
    def load(id, storage: dict):
        """
        Fetch an entire hdict

        >>> from hdict import _
        >>> from hdict.persistence.stored import Stored
        >>> fid = "1234567890123456789012345678901234567890"
        >>> did = "0000567890123456789012345678901234567890"
        >>> storage = {did: {"x": fid}, fid: Stored(5)}
        >>> d = (+_).load(did, storage)
        >>> d.show(colored=False)
        {
            x: ↑↓ cached at `dict`·,
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
        return frozenhdict.load(id, storage).unfrozen

    @staticmethod
    def fromfile(name, fields=None, format="df", named=None, hide_types=True):
        r"""
        Input format is defined by file extension: .arff, .csv

        >>> from hdict import hdict
        >>> from testfixtures import TempDirectory
        >>> arff = "@RELATION mini\n@ATTRIBUTE attr1	REAL\n@ATTRIBUTE attr2 	REAL\n@ATTRIBUTE class 	{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1"
        >>> with TempDirectory() as tmp:  # doctest:+ELLIPSIS
        ...    tmp.write("mini.arff", arff.encode())
        ...    d = hdict.fromfile(tmp.path + "/mini.arff")
        '/tmp/.../mini.arff'
        >>> d.show(colored=False)
        {
            df: "‹{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}, 'class': {0: '0', 1: '1'}}›",
            _id: YaEOJ7a7aOUux8qb1lY3mucUo6AU4vVv15JhAnn2,
            _ids: {
                df: Sxa-cdrwGU60j--6mK9FvWc7IaYdeYB-2yzSi62B
            }
        }
        >>> csv = "attr1,attr2,class\n5.1,3.5,0\n3.1,4.5,1"
        >>> with TempDirectory() as tmp:  # doctest:+ELLIPSIS
        ...    tmp.write("mini.csv", csv.encode())
        ...    d = hdict.fromfile(tmp.path + "/mini.csv")
        '/tmp/.../mini.csv'
        >>> d.show(colored=False)
        {
            df: "‹{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}, 'class': {0: 0, 1: 1}}›",
            _id: NPf36ZQWhyTj8yV3hVNjlKN3qJTNIxjgDJAkMWJY,
            _ids: {
                df: ytTKB-58EG6oWjgbY2-a-xyZJhBWUT.KESXVuFov
            }
        }
        """
        return frozenhdict.fromfile(name, fields, format, named, hide_types).unfrozen

    @staticmethod
    def fromtext(text: str, fields=None, format="df", named=None):
        r"""
        Input format is defined by file extension: .arff, .csv

        >>> from hdict import hdict
        >>> arff = "@RELATION mini\n@ATTRIBUTE attr1	REAL\n@ATTRIBUTE attr2 	REAL\n@ATTRIBUTE class 	{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1"
        >>> d = hdict.fromtext(arff)
        >>> d.show(colored=False)
        {
            df: "‹{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}›",
            _id: zkG1Kyr0K0matB3G0-BvKmIi2e.dHhA4zA6X6DwO,
            _ids: {
                df: FPE1eyMzyycW6Ue9SqyxaiakR3H3VDgzAFtwRlbl
            }
        }
        >>> csv = "attr1,attr2,class\n5.1,3.5,0\n3.1,4.5,1"
        >>> d = hdict.fromtext(csv)
        >>> d.show(colored=False)
        {
            df: "‹{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}, 'class': {0: 0, 1: 1}}›",
            _id: NPf36ZQWhyTj8yV3hVNjlKN3qJTNIxjgDJAkMWJY,
            _ids: {
                df: ytTKB-58EG6oWjgbY2-a-xyZJhBWUT.KESXVuFov
            }
        }
        """
        return frozenhdict.fromtext(text, fields, format, named).unfrozen

    @property
    def asdf(self):
        """
        Represent hdict as a DataFrame if possible

        >>> from hdict import hdict
        >>> d = hdict({"x": [1,2,3], "y": [5,6,7], "index": ["a", "b", "c"]})
        >>> d.asdf
           x  y
        a  1  5
        b  2  6
        c  3  7
        """
        return self.frozen.asdf

    @property
    def hoshes(self):
        """
        >>> from hdict import frozenhdict
        >>> [h.id for h in frozenhdict(x=3, y=2).hoshes.values()]
        ['KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29']
        """
        return self.frozen.hoshes

    def __bool__(self):
        return bool(self.frozen.data)

    def apply(self, appliable: apply | field, *applied_args, out=None, fhosh: Hosh = None, inplace=True, _sampleable=None, **applied_kwargs):
        if out is None:
            raise Exception(f"Missing output field name `out`")
        a = apply(appliable, *applied_args, fhosh=fhosh, _sampleable=_sampleable, **applied_kwargs)
        ao = a(*out) if isinstance(out, tuple) else a(out)
        frozen = self.frozen >> ao
        if inplace:
            self.frozen = frozen
        else:
            return frozen.unfrozen

    # def __reduce__(self):
    # return self.frozen.__reduce__()
