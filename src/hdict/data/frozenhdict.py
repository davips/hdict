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
from io import StringIO
from typing import TypeVar, Union

from hdict.dataset.dataset import loads, isplit
from hdict.dataset.pandas_handling import file2df
from hdict.text.customjson import CustomJSONEncoder, stringfy

VT = TypeVar("VT")


class frozenhdict(UserDict, dict[str, VT]):
    """
    Immutable hdict.

    Any nested 'hdict' value will be frozen to avoid inconsistency between the hdict id (inner id) and the frozenhdict id (outer id).

    >>> from hdict import frozenhdict, hdict
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
    >>> bool(d), bool(frozenhdict())
    (True, False)
    >>> d.data
    {'x': 3, 'y': 5}
    >>> from hdict import _, apply
    >>> d *= apply(lambda v, x: v - x).z
    >>> str(d)
    '⦑{x: 3, y: 5} » z=λ(v x)⦒'
    >>> d.show(colored=False)
    ⦑{
        x: 3,
        y: 5,
        _id: r5A2Mh6vRRO5rxi5nfXv1myeguGSTmqHuHev38qM,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2
        }
    } » z=λ(v x)⦒
    >>> d = {"v": 7} * d
    >>> d.solve().show(colored=False)
    {
        v: 7,
        x: 3,
        y: 5,
        z: λ(v x),
        _id: 0qFPOnULZigyiXU9Jv.1D.XSTIYHZ24UCT00DMHF,
        _ids: {
            v: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: 2-wfv1b9RyFHB2kdba3EBCy6Do5L-mMPJjT-nfPa
        }
    }
    >>> d = _ >> d
    >>> d.show(colored=False)
    {
        v: 7,
        x: 3,
        y: 5,
        z: λ(v x),
        _id: 0qFPOnULZigyiXU9Jv.1D.XSTIYHZ24UCT00DMHF,
        _ids: {
            v: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: 2-wfv1b9RyFHB2kdba3EBCy6Do5L-mMPJjT-nfPa
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
        _id: jZrJ2CiVUA9OqW.G7dwb3KoaTWGMUmSUVUXn0CkM,
        _ids: {
            a: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            v: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: 2-wfv1b9RyFHB2kdba3EBCy6Do5L-mMPJjT-nfPa
        }
    }
    >>> from hdict.content.entry import AbsEntry, Unevaluated
    >>> from hdict import frozenhdict
    """

    _evaluated = None
    _asdict, _asdicts, _asdicts_noid = None, None, None
    _hoshes = None

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _previous=None, **kwargs):
        from hdict.content.entry import AbsEntry
        from hdict.data.aux_frozendict import handle_identity
        from hdict.data.aux_frozendict import handle_items

        # todo: : check if _dictionary keys is 'str'; regex to check if k is an identifier;
        data = _dictionary or {}
        # REMINDER: Inside data, the only 'dict' entries are "_id" and "_ids", the rest are AbsEntry objects.
        self.data: dict[str, AbsEntry | str | dict[str, str]]
        self.data = handle_items(data, kwargs, previous=_previous)
        self.hosh, self.ids = handle_identity(self.data)
        self.id = self.hosh.id
        self.raw = self.data

    @property
    def hoshes(self):
        if self._hoshes is None:
            self._hoshes = {k: v.hosh for k, v in self.data.items()}
        return self._hoshes

    def __rmul__(self, left):
        from hdict import frozenhdict
        from hdict.expression.step.edict import EDict
        from hdict.expression.expr import Expr

        from hdict import hdict

        if isinstance(left, dict) and not isinstance(left, (hdict, frozenhdict)):
            return Expr(EDict(left), self)
        return NotImplemented  # pragma: no cover

    def __mul__(self, other):
        from hdict import hdict, frozenhdict
        from hdict.expression.step.edict import EDict
        from hdict.expression.expr import Expr
        from hdict.expression.step.step import AbsStep

        match other:
            case AbsStep() | hdict() | frozenhdict():
                return Expr(self, other)
            case dict():
                return Expr(self, EDict(other))
            case _:  # pragma: no cover
                return NotImplemented

    def __rrshift__(self, left):
        from hdict import hdict

        if isinstance(left, dict) and not isinstance(left, (hdict, frozenhdict)):
            return frozenhdict(left) >> self
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other):
        # If merging, keep ids.
        from hdict import hdict
        from hdict.expression.step.applyout import ApplyOut
        from hdict.expression.step.cache import cache
        from hdict.content.entry.cached import Cached

        from hdict.content.argument.apply import apply

        if isinstance(other, apply):  # pragma: no cover
            raise Exception(f"Cannot apply without specifying output(s).\n" f"Hint: d >> apply(f)('output_field1', 'output_field2')")
        from hdict.content.argument import AbsArgument

        if isinstance(other, AbsArgument):  # pragma: no cover
            raise Exception(f"Cannot pipe {type(other).__name__} without specifying output.\n" "Hint: d >> {'field name': object}\n" f"Hint: d['field name'] = object")

        from hdict.expression.expr import Expr

        match other:
            case hdict() | frozenhdict():
                dct = other.raw
            case ApplyOut(nested, out):
                dct = {out: nested}
            case cache(storage=storage, fields=fields):
                if not fields:
                    fields = (k for k, v in self.raw.items() if not v.isevaluated)
                dct = {k: Cached(self.ids[k], storage, self.raw[k]) for k in fields}
            case dict():
                dct = other
            case Expr():
                return Expr(self, other).solve()
            case _:  # pragma: no cover
                return NotImplemented
        return frozenhdict(dct, _previous=self)

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
        from hdict.content.entry import AbsEntry

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
        # todo: add flag to inhibit evaluation (i.e., fetching) of cached values; or other solution, e.g. Cache(write_onapply)
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
        from hdict.content.entry import AbsEntry

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

        # Put colors after json, to avoid escaping ansi codes.  todo: check how HTML behaves here
        for h in hoshes:
            txt = txt.replace(f'"{h.id}"', repr(h)) if colored else txt.replace(f'"{h.id}"', h.id)

        # Remove quotes.
        txt = re.sub(r'(": )"(λ.+?)"(?=,\n)', '": \\2', txt)  # Closure
        txt = re.sub(r'(": )"(·.+?)"(?=,\n)', '": \\2', txt)  # Wrapper
        txt = re.sub(r'(": )"(↑↓ cached at `.+?·)"(?=,\n)', '": \\2', txt)  # cache
        if not key_quotes:
            txt = re.sub(r'(?<!: )"([\-a-zA-Z0-9_ ]+?)"(?=: )', "\\1", txt)  # keys

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
        return self.data.keys()

    def values(self, evaluate=True):
        """Generator of field values"""
        return ((v.value if evaluate else v) for k, v in self.data.items())

    def items(self, evaluate=True):
        """Generator over field-value pairs"""
        for k, val in self.data.items():
            yield k, (val.value if evaluate else val)

    def save(self, storage: dict):
        """
        Store an entire frozenidict
        """
        from hdict.persistence.stored import Stored

        data = {self.id: self.ids}
        for field, fid in self.ids.items():
            value = self[field]
            if field.endswith("_"):
                raise Exception(f"Not implemented for mirror fields and is not possible for metafields")
                # todo:  confirm existence of the counterpart
                # data[kindid(fid)] = str(type(value))
            elif isinstance(value, frozenhdict):
                value.save(storage)
            else:
                data[fid] = Stored(value)
        # todo:  check if frozenhdict is being stored by mistake
        # todo:  attribute/method as subfield:
        #       apply(f, _.df.x)            SubField(name="df", attribute="x")
        #       apply(_.df.drop, "col1")    SubField(name="df", attribute="drop")
        #
        storage.update(data)

    @staticmethod
    def load(id, storage: dict, lazy=True) -> Union["frozenhdict", None]:
        """
        Fetch an entire frozenidict
        """
        if len(id) != 40:  # pragma: no cover
            raise Exception(f"id should have lenght of 40, not {len(id)}")
        return frozenhdict.fetch(id, storage, lazy, ishdict=True)

    @staticmethod
    def fetch(id: str, storage: dict, lazy=True, ishdict=False) -> Union["frozenhdict", None]:
        """
        Fetch a single entry

        When cache is a list, traverse it from the end (right item to the left item).
        """
        from hdict.content.entry.cached import Cached
        from hdict.persistence.stored import Stored

        if id not in storage:
            return None
            # if ishdict:
            #     raise Exception(f"hdict not saved or not cached if its nested.  `id` not found: `{id}`")
            # else:
            #     raise Exception(f"Entry not cached. `id` not found: `{id}`")
        obj = storage[id]
        if isinstance(obj, dict):
            ishdict = True  # Set to True, because now we have a nested frozenhdict
        elif ishdict or not isinstance(obj, Stored):  # pragma: no cover
            raise Exception(f"Wrong content for hdict expected under id {id}: {type(obj)}.")

        if ishdict:
            ids = obj
            data = {}
            mirrored = set()
            for field, fid in ids.items():
                if field.endswith("_"):
                    # TODO:  2023-06-23
                    #  -
                    raise Exception(f"Not implemented for mirror fields and is not possible for metafields")
                    # mirrored.add(field[:-1])
                    continue
                if lazy:
                    data[field] = Cached(fid, storage)
                else:
                    obj = frozenhdict.fetch(fid, storage, lazy=False, ishdict=False)
                    if obj is None:  # pragma: no cover
                        print(storage.keys())
                        raise Exception(f"Incomplete hdict: id '{id}' not found in the provided cache.")
                    data[field] = obj
            # for field in mirrored:
            #     obj = data[field]
            #     kind = obj.kind if isinstance(obj, Cached) else getkind(storage, obj.hosh)
            #     data[field + "_"] = handle_mirror(field, data, ids[field], kind)
            return frozenhdict.fromdict(data, ids)

        return obj.content

    @property
    def asdf(self):
        """
        Represent hdict as a DataFrame if possible
        """
        from pandas import DataFrame

        data = dict(self)
        index = data.pop("index")
        return DataFrame(data, index=index)

    @staticmethod
    def fromfile(name, fields=None, format="df", named=None, hide_types=True):
        r"""
        Input format is defined by file extension: .arff, .csv
        """
        from hdict.data.aux_frozendict import handle_format

        df, name = file2df(name, hide_types, True)
        return handle_format(format, fields, df, named and name)

    @staticmethod
    def fromtext(text: str, fields=None, format="df", named=None):
        r"""
        Input format is defined by file extension: .arff, .csv
        """
        from hdict import frozenhdict

        if text.startswith("@"):
            name = "<Unnamed>"
            with StringIO() as f:
                f.write(text)
                text = f.getvalue()
                df = loads(text)
                for line in isplit(text, "\n"):
                    if line[:9].upper() == "@RELATION":
                        name = line[9:].strip()
                        break
        else:
            from testfixtures import TempDirectory

            with TempDirectory() as tmp:
                tmp.write(
                    "temp.csv",
                    text.encode(),
                )
                return frozenhdict.fromfile(tmp.path + "/temp.csv", fields, format, named)

        from hdict.data.aux_frozendict import handle_format

        return handle_format(format, fields, df, named and name)

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
        return NotImplemented  # pragma: no cover

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return self.astext()

    def __str__(self):
        return stringfy(self.data)

    def __iter__(self):
        for k in self.data:
            yield k

    def __hash__(self):
        return hash(self.hosh)

    def __bool__(self):
        return bool(self.data)

    # def __reduce__(self):
    # dic = self.data.copy()
    # del dic["_id"]
    # del dic["_ids"]
    # return self.__class__, (dic,)
