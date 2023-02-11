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
from typing import TypeVar

from hdict.aux import handle_rshift
from hdict.content import MissingFieldException
from hdict.customjson import CustomJSONEncoder, stringfy
from hdict.pipeline import pipeline

VT = TypeVar("VT")


class frozenhdict(UserDict, dict[str, VT]):
    """
    Immutable hdict.

    Any nested 'hdict' value will be frozen to avoid inconsistency between the hdict id (inner id) and the frozenhdict id (outer id).

    >>> from hdict.frozenhdict import frozenhdict
    >>> d = frozenhdict({"x": 3}, y=5)
    >>> d.data
    {'x': 3, 'y': 5, '_id': 'r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM', '_ids': {'x': 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'y': 'ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2'}}
    >>> from hdict import _
    >>> d >>= _(lambda v, x: v - x).z
    >>> str(d)
    '{x: 3, y: 5, _id: "r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM", _ids: {x: "KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr", y: "ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2"}} » z=λ(v x)'
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        _id: r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2
        },
        v: ✗ missing ✗
    } » z=λ(v x)
    >>> d = {"v": 7} >> d
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
    >>> d = _() >> d
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
    {'a': 5} » {
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
    """

    _evaluated = None
    _asdict, _asdicts = None, None

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _previous=None, **kwargs):
        from hdict.content.handling import handle_values
        from hdict.content.abs.abscontent import AbsContent
        from hdict.content.handling import handle_identity

        if _previous is None:
            _previous = {}

        data = _dictionary or {}
        data.update(kwargs)
        if "_id" in data.keys() or "_ids" in data.keys():  # pragma: no cover
            raise Exception(f"Hosh-indexed dict cannot have a field named '_id'/'_ids': {data.keys()}")
        handle_values(data, _previous)

        # REMINDER: Inside data, the only 'dict' entries are "_id" and "_ids", the rest is AbsContent.
        self.data: dict[str, AbsContent | str | dict[str, str]] = data

        # REMINDER: "lazy hoshes" are only available after handling values (call above).
        self.hosh, self.ids = handle_identity(self.data)
        self.data["_id"] = self.id = self.hosh.id
        self.data["_ids"] = self.ids

    def __rrshift__(self, other):
        from hdict.hdict_ import hdict

        if isinstance(other, dict) and not isinstance(other, (hdict, frozenhdict)):
            return pipeline(hdict() >> other, self)
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other):
        from hdict.content.applyout import applyOut

        try:
            return handle_rshift(self, other)
        except MissingFieldException as e:
            # REMINDER: dict includes hdict/frozenhdict.
            if isinstance(other, (pipeline, dict, applyOut)):
                return pipeline(self, other, missing={self.id: e.args[0]})
            else:  # pragma: no cover
                print(type(other))
                raise e from None

    def __getitem__(self, item):  # pragma: no cover
        return self.data[item] if item in ["_id", "_ids"] else self.data[item].value

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
        from hdict.content.abs.abscontent import AbsContent
        from hdict.content.value import value

        data = {}
        for k, v in dictionary.items():
            if isinstance(v, AbsContent):
                if k in ids and ids[k] != v.id:  # pragma: no cover
                    raise Exception(f"Conflicting ids provided for key '{k}': ival.id={v.id}; ids[{k}]={ids[k]}")
                data[k] = v
            else:
                data[k] = value(v, ids[k] if k in ids else None)
        return frozenhdict(data)

    @property
    def evaluated(self):
        if self._evaluated is None:
            self._evaluated = self.evaluate()
        return self

    def evaluate(self):
        from hdict import apply

        for k, val in self.data.items():
            if isinstance(val, apply):
                val.evaluate()
        return self

    @property
    def asdict(self):
        """
        >>> from hdict import hdict, value
        >>> d = hdict.fromdict({"x": value(5, hosh="0123456789012345678901234567890123456789")}, {"x": "0123456789012345678901234567890123456789"})
        >>> d.asdict
        {'x': 5, '_id': 'bi5Qdbh-zgA1ZQdxGhxqjaKaQROtxk1VCPRZhMOq', '_ids': {'x': '0123456789012345678901234567890123456789'}}
        """
        if self._asdict is None:
            dic = {k: v for k, v in self.items()}
            dic["_id"] = self.id
            dic["_ids"] = self.ids.copy()
            self._asdict = dic
        return self._asdict

    @property
    def asdicts(self):
        """
        Recurse into nested frozenhdicts (REMINDER: hdict is never nested)

        >>> from hdict import value, hdict
        >>> d = hdict(x=value(5, hosh="0123456789012345678901234567890123456789"))
        >>> d.asdicts
        {'x': 5, '_id': 'bi5Qdbh-zgA1ZQdxGhxqjaKaQROtxk1VCPRZhMOq', '_ids': {'x': '0123456789012345678901234567890123456789'}}
        """
        if self._asdicts is None:
            dic = {}
            for k, v in self.items():
                dic[k] = v.asdicts if isinstance(v, frozenhdict) else v
            dic["_id"] = self.id
            dic["_ids"] = self.ids.copy()
            self._asdicts = dic
        return self._asdicts

    @property
    def asdicts_hoshes_noneval(self):
        from hdict.content.abs.abscloneable import AbsCloneable

        hoshes = set()
        dic = {}
        for k, val in self.data.items():
            if k not in ["_id", "_ids"]:
                hoshes.add(val.hosh)
                if isinstance(val, AbsCloneable):
                    dic[k] = val
                else:
                    v = val.value
                    if isinstance(v, frozenhdict):
                        dic[k], subhoshes = v.asdicts_hoshes_noneval
                        hoshes.update(subhoshes)
                    else:
                        dic[k] = v
        hoshes.add(self.hosh)
        dic["_id"] = self.id
        dic["_ids"] = self.ids.copy()
        return dic, hoshes

    def astext(self, colored=True, key_quotes=False, extra_items=None):
        r"""Textual representation of a frozenidict object"""
        dicts, hoshes = self.asdicts_hoshes_noneval
        if extra_items:
            dicts.update(extra_items)
        txt = json.dumps(dicts, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)

        # Put colors after json, to avoid escaping ansi codes.  TODO: check how HTML behaves here
        for h in hoshes:
            txt = txt.replace(f'"{h.id}"', repr(h)) if colored else txt.replace(f'"{h.id}"', h.id)
        txt = re.sub(r'(": )"(λ.+?)"(?=,\n)', '": \\2', txt)
        if not key_quotes:
            txt = re.sub(r'(?<!: )"([\-a-zA-Z0-9_ ]+?)"(?=: )', "\\1", txt)
        if extra_items:
            for v in extra_items.values():
                txt = txt.replace(f'"{v}"', f"{v}")
        return txt

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
        return (k for k in self.data if not k.startswith("_"))

    def values(self, evaluate=True):
        """Generator of field values (keys that don't start with '_')"""
        return ((v.value if evaluate else v) for k, v in self.data.items() if not k.startswith("_"))

    def items(self, evaluate=True):
        """Generator over field-value pairs"""
        for k, val in self.data.items():
            if not k.startswith("_"):
                yield k, (val.value if evaluate else val)

    # @cached_property
    # def aslist(self):
    #     return list(self.values())
    #
    # @staticmethod
    # def fromid(id, cache) -> Union["frozenhdict", None]:
    #     return frozenhdict.fetch(id, cache, isidict=True)
    #
    # @staticmethod
    # def fetch(id, cache, isidict=False) -> Union["frozenhdict", None]:
    #     caches = cache if isinstance(cache, list) else [cache]
    #     while id not in (cache := caches.pop(0)):
    #         if not caches:
    #             raise Exception(f"id '{id}' not found in the provided cache {cache.keys()}.")
    #
    #     obj = cache[id]
    #     if isinstance(obj, dict):
    #         if "_ids" not in obj:
    #             raise Exception(f"Wrong content for idict under id {id}: missing '_ids' fields ({obj.keys()}).")
    #         isidict = True
    #     elif isidict:
    #         raise Exception(f"Wrong content for idict expected under id {id}: {type(obj)}.")
    #
    #     # TODO: adopt lazy fetch: CacheableiVal as 'return' value
    #     if isidict:
    #         ids = obj["_ids"]
    #         data = {}
    #         for k, v in ids.items():
    #             data[k] = frozenhdict.fetch(v, cache)
    #         return frozenhdict.fromdict(data, ids)
    #     return obj

    def __eq__(self, other):
        if isinstance(other, dict):
            if "_id" in other:
                return self.id == other["_id"]
            if list(self.keys()) != list(other.keys()):
                return False
        if isinstance(other, dict):
            self.evaluate()
            data = self.asdict
            del data["_id"]
            del data["_ids"]
            return data == other
        raise TypeError(f"Cannot compare {type(self)} and {type(other)}")  # pragma: no cover

    def __ne__(self, other):
        return not (self == other)

    # def __reduce__(self):
    #     # TODO: pickling idicts shouldn't be necessary after cache[id]=DFiVal is implemented
    #     dic = self.data.copy()
    #     ids = dic.pop("_ids").copy()
    #     del dic["_id"]
    #     return self.fromdict, (dic, ids)

    def __repr__(self):
        return self.astext()

    def __str__(self):
        return stringfy(self.data)

    def __iter__(self):
        for k in self.data:
            if not k.startswith("_"):
                yield k

    def __hash__(self):
        return hash(self.hosh)

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
