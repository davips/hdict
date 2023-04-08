from itertools import chain
from typing import Dict
from typing import TypeVar

from hosh import ø

from hdict import hdict, value, frozenhdict
from hdict.abs import AbsAny
from hdict.applyout import ApplyOut
from hdict.content.argument.apply import apply
from hdict.content.argument.field import field
from hdict.content.argument.sample import sample
from hdict.content.entry import AbsEntry
from hdict.pandas_handling import explode_df

VT = TypeVar("VT")


class MissingFieldException(Exception):
    pass


def handle_items(*datas: [Dict[str, object]], previous: [Dict[str, AbsEntry]]):
    result = previous.copy()
    result__mirror_fields = {}
    for key, item in chain(*(data.items() for data in datas)):
        entry = handle_item(key, item, result)
        if isinstance(key, str) and key.endswith("_"):
            result__mirror_fields[f"{key[:-1]}"] = value(entry.hdict, entry.hosh)
        if isinstance(entry, dict):
            result.update(entry)
        else:
            result[key] = entry
    result.update(result__mirror_fields)
    return result


def handle_item(key, item, previous):
    if isinstance(key, tuple):
        from hdict.multioutput import handle_multioutput

        return handle_multioutput(previous, key, item)
    elif not isinstance(key, str):  # pragma: no cover
        raise Exception(f"Invalid type for input field specification: {type(key).__name__}")
    elif key.startswith("_"):  # pragma: no cover
        raise Exception(f"Field names cannot start with '_': {key}")

    match item:
        case AbsEntry():
            return item
        case field(name=name):
            if name not in previous:
                raise MissingFieldException(f"Missing field `{name}`")
            return handle_item(name, previous[name], previous)
        case apply():
            return item.enclosure(previous, key)
        case sample():
            raise Exception(f"Unsampled variable or argument `{key}`")
        case frozenhdict():
            return value(item, item.hosh)
        case hdict():
            return value(item.frozen, item.hosh)
        case ApplyOut():
            raise Exception("Cannot assign output through both apply and dict-key: '>> {out: apply(...)(out)}'.")
        case AbsAny():
            raise Exception(f"Cannot handle instance of type '{type(item).__name__}'.")
        case _ if str(type(item)) == "<class 'pandas.core.frame.DataFrame'>":
            return explode_df(item)
        case _:
            return value(item)


def handle_identity(data):
    hosh = ø
    ids = {}
    for k, v in data.items():
        # Handle meta. mirror, and field ids differently.
        if k.startswith("_"):  # pragma: no cover
            raise Exception("Custom metafields are not allowed:", k)
            # self.mhosh += self.data[k].hosh * k.encode()                # self.mids[k] = self.data[k].hosh.id
        elif k.endswith("_"):
            # mirrorfield, e.g.: 'df_' is a mirror/derived from 'df'
            pass
        else:
            hosh += data[k].hosh * k.encode()
            # PAPER REMINDER: state in the paper that hash(identifier) must be different from hash(value), for any identifier and value. E.g.: hash(X) != hash("X")    #   Here the difference always happen because values are pickled, while identifiers are just encoded().
            ids[k] = data[k].hosh.id
    return hosh, ids
