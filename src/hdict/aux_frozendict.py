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
from hdict.content.entry.ready import AbsReadyEntry
from hdict.content.entry.unready.delayed import DelayedEntry, DelayedMultiEntry
from hdict.content.entry.unready.missing import MissingEntry
from hdict.content.entry.unready.unsampled import UnsampledEntry
from hdict.pandas_handling import explode_df

VT = TypeVar("VT")


def check_entry(entry):
    missing, unsampled = False, False
    match entry:
        case MissingEntry() | DelayedEntry() | DelayedMultiEntry():
            missing = True
        case UnsampledEntry():
            unsampled = True
    return missing, unsampled


def handle_items(*datas: [Dict[str, object]], result=None, ignore=None):
    if result is None:
        result = {}
    if ignore is None:
        ignore = set()
    result__mirror_fields = {}
    missing, unsampled = False, False
    for k, item in chain(*(data.items() for data in datas)):
        before = set(result.keys())
        entry = handle_item(item, result,  ignore)
        if entry is None:
            continue
        missing_, unsampled_ = check_entry(entry)  # TODO: ver que chamador de handle_item() requer esse check
        missing, unsampled = missing or missing_, unsampled or unsampled_

        if isinstance(k, tuple):
            from hdict.multioutput import handle_multioutput
            from hdict.content.entry.unready import AbsUnreadyEntry
            if isinstance(entry, AbsUnreadyEntry):
                from hdict.multioutput import loop_field_names
                keys = []
                for key, i, source in loop_field_names(k):
                    keys.append(key)
                    prevent_overwriting_unready(key, DelayedMultiEntry(k, item, keys), result, ignore)
                    ignore.add(key)
            else:
                _, missing_, unsampled_ = handle_multioutput(result, k, entry, ignore)
                missing, unsampled = missing or missing_, unsampled or unsampled_
            continue
        elif not isinstance(k, str):  # pragma: no cover
            raise Exception(f"Invalid type for input field specification: {k.__class__.__name__}")
        elif k.endswith("_"):
            result__mirror_fields[f"{k[:-1]}"] = value(entry.hdict, entry.hosh)
        elif k.startswith("_"):  # pragma: no cover
            raise Exception(f"Field names cannot start with '_': {k}")

        after = set(result.keys())
        new = after.difference(before)
        if k in new:
            del result[k]
        prevent_overwriting_unready(k, entry, result, ignore)
    result.update(result__mirror_fields)
    return result, missing, unsampled


def handle_item(item, result, ignore):
    """
    Transform items into entries

    Create unready entries inside `result` when needed:
        DelayedEntry with related MissingEntry's
        UnsampledEntry
    """
    match item:
        case AbsReadyEntry() | MissingEntry() | UnsampledEntry():
            return item  # REMINDER: MissingEntry wasn't fixed at frozenhdict.rshift
        case DelayedEntry(argument):
            return handle_item(argument, result, ignore)  # REMINDER: this tries to fix it this time
        case DelayedMultiEntry(keys, argument, fields):
            _, missing, unsampled = handle_items({keys: argument}, result=result, ignore=ignore)
            if missing or unsampled:
                return item
        case field(name=name):
            if name in result:
                return handle_item(result[name], result, ignore)
            result[name] = MissingEntry()
            return DelayedEntry(item)
        case apply():
            if item.sampleable:
                return UnsampledEntry(item)
            closure = item.enclosure(result, ignore)  # REMINDER: this creates MissingEntry for DelayedEntry below
            if closure.unready:
                return DelayedEntry(item)
            return closure
        case sample():
            return UnsampledEntry(item)
        case hdict() | frozenhdict():
            if item.sampleable:
                return UnsampledEntry(item)
            if item.hasmissing:
                # item.show()
                raise Exception(f"Cannot nest a hdict with missing fields.")
            return value(item, item.hosh)
        case ApplyOut():
            raise Exception("Cannot assign output through both apply and dict-key: '>> {out: apply(...)(out)}'.")
        case AbsAny():
            raise Exception(f"Cannot handle instance of type '{item.__class__.__name__}'.")
        case _ if str(type(item)) == "<class 'pandas.core.frame.DataFrame'>":
            return explode_df(item)
        case _:
            return value(item)


def handle_identity(data, unready):
    hosh = ø
    ids = {}
    if unready:
        for k, v in data.items():
            match v:
                case AbsReadyEntry():
                    ids[k] = data[k].hosh.id
                case MissingEntry():
                    ids[k] = "✗ missing"
                case UnsampledEntry():
                    ids[k] = "✗ unsampled"
                case DelayedEntry():
                    ids[k] = "✗ delayed"
                case DelayedMultiEntry(fields=fields):
                    ids[k] = f"✗ delayed ({','.join(fields)})"
    else:
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


def prevent_overwriting_unready(k, v, data, ignore):
    from hdict.content.entry.unready import AbsUnreadyEntry
    if k in data:
        if isinstance(data[k], AbsUnreadyEntry) and k not in ignore:
            raise Exception(f"Cannot overwrite a `{data[k].__class__.__name__}` field ('{k}').\n"
                            "Hint: provide the missing value from the left side:\n"
                            "`{'" + k + "': «missing value»} >> d`.")
        if isinstance(v, MissingEntry):
            return
    data[k] = v
