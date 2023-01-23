import json
import re
from collections import UserDict
from functools import cached_property
from typing import Dict, TypeVar

from hdict.customjson import CustomJSONEncoder
from hosh import ø

VT = TypeVar("VT")


class frozenhdict(UserDict, Dict[str, VT]):
    """
    Immutable hdict.

    Any nested 'hdict' value will be frozen to avoid inconsistency between the hdict id (inner id) and the frozenhdict id (outer id).

    >>> from hdict.frozenhdict import frozenhdict
    >>> d = frozenhdict({"x": 3}, y=5)
    >>> d.data
    {'x': 3, 'y': 5, '_id': 'r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM', '_ids': {'x': 'KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr', 'y': 'ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2'}}

    """

    _evaluated = None

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, **kwargs):
        from hdict.entry.absarg import AbsArg
        data: Dict[str, AbsArg] = _dictionary or {}
        data.update(kwargs)
        if "_id" in data.keys() or "_ids" in data.keys():  # pragma: no cover
            raise Exception(f"Hosh-indexed dict cannot have a field named '_id'/'_ids': {data.keys()}")
        from hdict.entry.handling import handle_values
        self.data = handle_values(data)  # REMINDER: 'dict' entries are only "_id" and "_ids".

        # REMINDER: "lazy hoshes" are only available after handling values (call above).
        self.hosh = ø
        self.ids = {}
        for k, v in self.data.items():
            # Handle meta. mirror, and field ids differently.
            if k.startswith("_"):
                # TODO: add mehosh (for metafields)? # TODO: add mihosh (for mirrorfields)?
                raise NotImplementedError(k)
                # self.mhosh += self.data[k].hosh * k.encode()                # self.mids[k] = self.data[k].hosh.id
            elif k.endswith("_"):
                # TODO: specify new type of field: mirrorfield, e.g.: 'df_' is a mirror/derived from 'df'
                raise NotImplementedError()
            else:
                self.hosh += self.data[k].hosh * k.encode()
                # PAPER REMINDER: state in the paper that hash(identifier) must be different from hash(value), for any identifier and value. E.g.: hash(X) != hash("X")    #   Here the difference always happen because values are pickled, while identifiers are just encoded().
                self.ids[k] = self.data[k].hosh.id

        self.data["_id"] = self.id = self.hosh.id
        self.data["_ids"] = self.ids

        # minor TODO: if there are duplicate ids in hdict, use the same AbsVal.value reference for all (cannot use the AbsVal obj directly due to the flag 'ispositional')

    def __rshift__(self, other):
        from hdict import hdict
        data = self.data.copy()
        del data["_id"]
        del data["_ids"]
        if isinstance(other, hdict):  # merge keeping ids
            other = other.frozen
        if isinstance(other, frozenhdict):  # merge keeping ids
            other = other.data
        if isinstance(other, dict):  # merge keeping ids of Val objects if any is present
            for k, v in other.items():
                if isinstance(k, tuple):  # TODO
                    pass
                #     data.update(multifield(k, v))
                elif isinstance(k, str):
                    data[k] = v
                else:
                    raise Exception(f"Invalid type for input field specification: {type(k)}")
            return frozenhdict(data)

    def __getitem__(self, item):
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
        """Build a frozenidict from values and pre-defined ids"""
        from hdict.entry.absarg import AbsArg
        from hdict import value
        data = {}
        for k, v in dictionary.items():
            if isinstance(v, AbsArg):
                if k in ids and ids[k] != v.id:  # pragma: no cover
                    raise Exception(f"Conflicting ids provided for key '{k}': ival.id={v.id}; ids[{k}]={ids[k]}")
                data[k] = v
            else:
                data[k] = value(v, ids[k])
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

    @cached_property
    def asdict(self):
        dic = {k: v for k, v in self.items()}
        dic["_id"] = self.id
        dic["_ids"] = self.ids.copy()
        return dic

    @cached_property
    def asdicts(self):
        dic = {}
        for k, v in self.entries():
            dic[k] = v.asdicts if isinstance(v, frozenhdict) else v
        dic["_id"] = self.id
        dic["_ids"] = self.ids.copy()
        return dic

    @cached_property
    def asdicts_hoshes_noneval(self):
        from hdict import apply
        hoshes = set()
        dic = {}
        for k, val in self.data.items():
            if k not in ["_id", "_ids"]:
                hoshes.add(val.hosh)
                if isinstance(val, apply):
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

    def astext(self, colored=True, key_quotes=False):
        r"""Textual representation of a frozenidict object"""
        dicts, hoshes = self.asdicts_hoshes_noneval
        txt = json.dumps(dicts, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)

        # Put colors after json, to avoid escaping ansi codes.
        if colored:
            for h in hoshes:
                txt = txt.replace(f'"{h.id}"', h.idc)
        txt = re.sub(r'(": )"(λ.+?)"(?=,\n)', '": \\2', txt)
        if not key_quotes:
            txt = re.sub(r'(?<!: )"([a-zA-Z0-9_ ]+?)"(?=: )', "\\1", txt)
        return txt

    def show(self, colored=True, key_quotes=False):
        r"""Print textual representation of a frozenidict object"""
        print(self.astext(colored, key_quotes))

    def copy(self):  # pragma: no cover
        raise Exception("A FrozenIdict doesn't need copies")

    @property
    def unfrozen(self):
        from hdict import hdict
        return hdict(_frozen__cache=self)

    # def entries(self, evaluate=True):
    #     """Iterator over all items"""
    #     yield from self.items(evaluate)
    #     # yield from self.metaitems(evaluate)

    def keys(self):
        """Generator of keys which don't start with '_'"""
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

    def __reduce__(self):
        # TODO: pickling idicts shouldn't be necessary after cache[id]=DFiVal is implemented
        dic = self.data.copy()
        ids = dic.pop("_ids").copy()
        del dic["_id"]
        return self.fromdict, (dic, ids)

    def __repr__(self):
        return self.astext()

    def __str__(self):
        js = json.dumps(self.data, ensure_ascii=False, cls=CustomJSONEncoder)
        return re.sub(r'(?<!: )"(\S*?)"', "\\1", js)

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