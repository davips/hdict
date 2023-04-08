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

import json
import re
from collections import UserDict
from typing import TypeVar, Union

from hdict.content.entry import AbsEntry
from hdict.customjson import CustomJSONEncoder, stringfy

VT = TypeVar("VT")


class frozenhdict(UserDict, dict[str, VT]):
    """
    Immutable hdict.

    Any nested 'hdict' value will be frozen to avoid inconsistency between the hdict id (inner id) and the frozenhdict id (outer id).

    >>> from hdict.frozenhdict import frozenhdict
    >>> d = frozenhdict({"x": 3}, y=5)
    >>> from hosh._internals_appearance import decolorize
    >>> print(decolorize(repr(d)))  # This is equivalent to just 'd', without colors.
    {
        x: 3,
        y: 5,
        _id: r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2
        }
    }
    >>> d.data
    {'x': 3, 'y': 5}
    >>> from hdict import _, apply
    >>> d *= apply(lambda v, x: v - x).z
    >>> str(d)
    '{x: 3, y: 5} » z=λ(v x)'
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        _id: r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2
        }
    } » z=λ(v x)
    >>> d = {"v": 7} * d
    >>> d.solve().show(colored=False)
    {
        v: 7,
        x: 3,
        y: 5,
        z: λ(v x),
        _id: -a24f2g4z-c-tPEss6G8WEd7h8zMopCCsCdQowjL,
        _ids: {
            v: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: .beBfajsUjKto9qdBCKsLmBgsaNPpJiyz24P9.qg
        }
    }
    >>> d = _ >> d
    >>> d.show(colored=False)
    {
        v: 7,
        x: 3,
        y: 5,
        z: λ(v x),
        _id: -a24f2g4z-c-tPEss6G8WEd7h8zMopCCsCdQowjL,
        _ids: {
            v: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: .beBfajsUjKto9qdBCKsLmBgsaNPpJiyz24P9.qg
        }
    }
    >>> d = {"a": 5} >> d
    >>> d.show(colored=False)
    {
        a: 5,
        v: 7,
        x: 3,
        y: 5,
        z: λ(v x),
        _id: ELQZugqdug6eCOLZSPaimnGqgmhRjJoDLD8cOlYR,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            v: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: .beBfajsUjKto9qdBCKsLmBgsaNPpJiyz24P9.qg
        }
    }
    """

    _evaluated = None
    _asdict, _asdicts, _asdicts_noid = None, None, None

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _previous=None, **kwargs):
        from hdict.content.entry import AbsEntry
        from hdict.aux_frozendict import handle_identity
        from hdict.aux_frozendict import handle_items

        if _previous is None:
            _previous = {}

        # TODO: check if _dictionary keys is 'str'; regex to check if k is an identifier;
        data = _dictionary or {}
        # REMINDER: Inside data, the only 'dict' entries are "_id" and "_ids", the rest are AbsEntry objects.
        self.data: dict[str, AbsEntry | str | dict[str, str]]
        self.data = handle_items(data, kwargs, previous=_previous)
        self.hosh, self.ids = handle_identity(self.data)
        self.id = self.hosh.id

    def __rrshift__(self, other):
        from hdict import hdict

        if isinstance(other, dict) and not isinstance(other, (hdict, frozenhdict)):
            return frozenhdict(other) >> self
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other):
        from hdict import hdict
        from hdict.applyout import ApplyOut

        # Merge keeping ids.
        if isinstance(other, hdict):
            other = other.frozen
        if isinstance(other, frozenhdict):
            other = other.data
        if isinstance(other, ApplyOut):
            other = {other.out: other.nested}

        if isinstance(other, dict):
            return frozenhdict(other, _previous=self.data)
        return NotImplemented  # pragma: no cover

    def __getitem__(self, item):  # pragma: no cover
        return self.data[item].value

    def __getattr__(self, item):  # pragma: no cover
        if item in self.data:
            return self.data[item].value
        return self.__getattribute__(item)

    def __setitem__(self, key: str, value):  # pragma: no cover
        print(value)
        raise Exception(f"Cannot set an entry ({key}) of a frozen dict.")

    def __delitem__(self, key):  # pragma: no cover
        raise Exception(f"Cannot delete an entry ({key}) from a frozen dict.")

    @staticmethod
    def fromdict(dictionary, ids):
        """Build a frozenidict from values and pre-defined ids

        >>> from hdict import hdict, value
        >>> hdict.fromdict({"x": value(5, hosh="0123456789012345678901234567890123456789")}, {"x": "0123456789012345678901234567890123456789"}).show(colored=False)
        {
            x: 5,
            _id: bi5Qdbh-zgA1ZQdxGhxqjaKaQROtxk1VCPRZhMOq,
            _ids: {
                x: 0123456789012345678901234567890123456789
            }
        }
        """
        from hdict.content.value import value

        data = {}
        for k, v in dictionary.items():
            if isinstance(v, AbsEntry):
                if k in ids and ids[k] != v.id:  # pragma: no cover
                    raise Exception(f"Conflicting ids provided for key '{k}': ival.id={v.id}; ids[{k}]={ids[k]}")
                data[k] = v
            else:
                data[k] = value(v, ids[k] if k in ids else None)
        return frozenhdict(data)

    @property
    def evaluated(self):
        if self._evaluated is None:
            for k, val in self.data.items():
                val.evaluate()
            self._evaluated = self
        return self

    def evaluate(self):
        _ = self.evaluated

    @property
    def asdict(self):
        """
        Convert to 'dict', including ids.

        This evaluates all fields.
        HINT: Use 'dict(d)' to convert a 'hdict' to a 'dict' excluding ids.

        >>> from hdict import hdict, value
        >>> d = hdict.fromdict({"x": value(5, hosh="0123456789012345678901234567890123456789")}, {"x": "0123456789012345678901234567890123456789"})
        >>> d.asdict
        {'x': 5, '_id': 'bi5Qdbh-zgA1ZQdxGhxqjaKaQROtxk1VCPRZhMOq', '_ids': {'x': '0123456789012345678901234567890123456789'}}
        """
        if self._asdict is None:
            dic = dict(self.items())
            dic["_id"] = self.id
            dic["_ids"] = self.ids.copy()
            self._asdict = dic
        return self._asdict

    @property
    def asdicts(self):
        """
        Convert to 'dict' recursing into nested frozenhdicts, including ids.

        This evaluates all fields.
        REMINDER: hdict is never nested, frozenhdict is used instead
        HINT: Use 'asdicts_noid' to recursively convert a 'hdict' to a 'dict' excluding ids.

        >>> from hdict import value, hdict
        >>> d = hdict(x=value(5, hosh="0123456789012345678901234567890123456789"))
        >>> e = hdict(d=d)
        >>> e.asdicts
        {'d': {'x': 5, '_id': 'bi5Qdbh-zgA1ZQdxGhxqjaKaQROtxk1VCPRZhMOq', '_ids': {'x': '0123456789012345678901234567890123456789'}}, '_id': 'GGhKhUmGhISaoHevn39hb-pLZEMoAc3KzE6Z0.IH', '_ids': {'d': 'bi5Qdbh-zgA1ZQdxGhxqjaKaQROtxk1VCPRZhMOq'}}
        >>> dict(e) == e
        True
        """
        if self._asdicts is None:
            from hdict import hdict

            dic = {}
            for k, v in self.items():
                dic[k] = v.asdicts if isinstance(v, (hdict, frozenhdict)) else v
            dic["_id"] = self.id
            dic["_ids"] = self.ids.copy()
            self._asdicts = dic
        return self._asdicts

    @property
    def asdicts_noid(self):
        """
        Convert to 'dict' recursing into nested frozenhdicts, excluding ids.

        REMINDER: hdict is never nested, frozenhdict is used instead
        HINT: Use 'asdicts' to recursively convert a 'hdict' 'd' to 'dict' including ids.

        >>> from hdict import value, hdict
        >>> d = hdict(x=value(5, hosh="0123456789012345678901234567890123456789"))
        >>> e = hdict(d=d)
        >>> e.asdicts_noid
        {'d': {'x': 5}}
        >>> dict(e) == e
        True

        """
        if self._asdicts_noid is None:
            from hdict import hdict

            dic = {}
            for k, v in self.items():
                dic[k] = v.asdicts_noid if isinstance(v, (hdict, frozenhdict)) else v
            self._asdicts_noid = dic
        return self._asdicts_noid

    @property
    def asdicts_hoshes_noneval(self):
        from hdict import value

        hoshes = set()
        dic = {}
        for k, val in self.data.items():
            if isinstance(val, AbsEntry):
                hoshes.add(val.hosh)
            if isinstance(val, value):
                v = val.value
                if isinstance(v, frozenhdict):
                    dic[k], subhoshes = v.asdicts_hoshes_noneval
                    hoshes.update(subhoshes)
                else:
                    dic[k] = v
            else:
                dic[k] = val
        hoshes.add(self.hosh)
        dic["_id"] = self.id
        dic["_ids"] = self.ids.copy()
        return dic, hoshes

    def astext(self, colored=True, key_quotes=False):
        r"""Textual representation of a frozenidict object"""
        dicts, hoshes = self.asdicts_hoshes_noneval
        txt = json.dumps(dicts, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)

        # Put colors after json, to avoid escaping ansi codes.  TODO: check how HTML behaves here
        for h in hoshes:
            txt = txt.replace(f'"{h.id}"', repr(h)) if colored else txt.replace(f'"{h.id}"', h.id)
        txt = re.sub(r'(": )"(λ.+?)"(?=,\n)', '": \\2', txt)
        if not key_quotes:
            txt = re.sub(r'(?<!: )"([\-a-zA-Z0-9_ ]+?)"(?=: )', "\\1", txt)
        return txt.replace('"§«§lazy', "").replace('lazy§«§"', "")

    def show(self, colored=True, key_quotes=False):
        r"""Print textual representation of a frozenidict object"""
        print(self.astext(colored, key_quotes))

    def copy(self):  # pragma: no cover
        raise Exception("A FrozenIdict doesn't need copies")

    @property
    def unfrozen(self):
        from hdict import hdict

        return hdict(_frozen=self)

    # def entries(self, evaluate=True):
    #     """Iterator over all items"""
    #     yield from self.items(evaluate)
    #     # yield from self.metaitems(evaluate)

    def keys(self):
        """Generator of keys which don't start with '_'"
        >>> from hdict import hdict
        >>> list(hdict(x=3, y=5).keys())
        ['x', 'y']
        >>> list(hdict(x=3, y=5).values())
        [3, 5]
        """
        # return (k for k in self.data if not k.startswith("_"))
        return self.data.keys()

    def values(self, evaluate=True):
        """Generator of field values (keys that don't start with '_')"""
        return ((v.value if evaluate else v) for k, v in self.data.items())
        # return ((v.value if evaluate else v) for k, v in self.data.items() if not k.startswith("_"))

    def items(self, evaluate=True):
        """Generator over field-value pairs"""
        for k, val in self.data.items():
            # if not k.startswith("_"):
            yield k, (val.value if evaluate else val)

    def save(self, cache: dict):
        """
        Store an entire frozenidict
        """
        data = {self.id: self.ids}
        for field, fid in self.ids.items():
            value = self[field]
            if isinstance(value, frozenhdict):
                value.save(cache)
            else:
                data[fid] = value
        cache.update(data)

    @staticmethod
    def load(id, cache: dict | list, lazy=True) -> Union["frozenhdict", None]:
        """
        Fetch an entire frozenidict
        """
        if len(id) != 40:  # pragma: no cover
            raise Exception(f"id should have lenght of 40, not {len(id)}")
        return frozenhdict.fetch(id, cache, lazy, ishdict=True)

    @staticmethod
    def fetch(id, cache, lazy=True, ishdict=False) -> Union["frozenhdict", None]:
        """
        Fetch a single entry

        When cache is a list, traverse it from the end (right item to the left item).
        """
        from hdict.content.entry.lazy import Lazy

        caches = cache if isinstance(cache, list) else [cache]
        while id not in (cache := caches.pop()):
            if not caches:
                raise Exception(f"id '{id}' not found in the provided cache {cache.keys()}.")
        obj = cache[id]
        if isinstance(obj, dict):
            ishdict = True  # Set to True, because now we have a nested frozenhdict
        elif ishdict:
            raise Exception(f"Wrong content for idict expected under id {id}: {type(obj)}.")

        if ishdict:
            ids = obj
            data = {}
            for field, fid in ids.items():
                data[field] = Lazy(fid, cache) if lazy else frozenhdict.fetch(fid, cache, lazy, False)
            return frozenhdict.fromdict(data, ids)
        return obj

    def __eq__(self, other):
        if isinstance(other, dict):
            if "_id" in other:
                return self.id == other["_id"]
            if list(self.keys()) != list(other.keys()):
                return False
            from hdict import hdict

            if isinstance(other, (frozenhdict, hdict)):
                return self.id == other.id
            return dict(self) == other
        raise TypeError(f"Cannot compare {type(self).__name__} and {type(other).__name__}")  # pragma: no cover

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return self.astext()

    def __str__(self):
        return stringfy(self.data)

    def __iter__(self):
        for k in self.data:
            # if not k.startswith("_"):
            yield k

    def __hash__(self):
        return hash(self.hosh)

    def __mul__(self, other):
        from hdict.expr import Expr

        return Expr(self, other)

    # def metakeys(self):
    #     """Generator of keys which start with '_'"""
    #     return (k for k in self.data if k.startswith("_") and k not in ["_id", "_ids"])
    #
    # def metavalues(self, evaluate=True):
    #     """Generator of field values (keys don't start with '_')"""
    #     return ((v.value if evaluate else v) for k, v in self.data.items() if k.startswith("_") and k not in ["_id", "_ids"])
    #
    # def metaitems(self, evaluate=True):
    #     """Generator over field-value pairs"""
    #     for k, ival in self.data.items():
    #         if k.startswith("_") and k not in ["_id", "_ids"]:
    #             yield k, (ival.value if evaluate else ival)
    #
    # def entries(self, evaluate=True):
    #     """Iterator over all items"""
    #     yield from self.items(evaluate)
    #     yield from self.metaitems(evaluate)
    #
    # @cached_property
    # def fields(self):
    #     return list(self.keys())
    #
    # @cached_property
    # def metafields(self):
    #     """List of keys which start with '_'"""
    #     return [k for k in self.data if k.startswith("_") and k not in ["_id", "_ids"]]
