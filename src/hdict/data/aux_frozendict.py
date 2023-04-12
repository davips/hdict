from itertools import chain
from typing import Dict
from typing import TypeVar

from hosh import ø

from hdict import hdict, value, frozenhdict
from hdict.abs import AbsAny
from hdict.content.argument.apply import apply
from hdict.content.argument.field import field
from hdict.content.argument.sample import sample
from hdict.content.entry import AbsEntry
from hdict.content.entry.closure import Closure
from hdict.dataset.dataset import df2Xy
from hdict.expression.step.applyout import ApplyOut

VT = TypeVar("VT")


class MissingFieldException(Exception):
    pass


def handle_items(*datas: [Dict[str, object]], previous: [Dict[str, AbsEntry]]):
    result = previous.copy()
    result__mirror_fields = {}
    for key, item in chain(*(data.items() for data in datas)):
        entry = handle_item(key, item, result)
        if isinstance(key, str) and key.endswith("_") and isinstance(entry, value):
            result__mirror_fields[f"{key[:-1]}"] = value(entry.hdict, entry.hosh)
        if isinstance(entry, dict):
            result.update(entry)
        else:
            result[key] = entry
    result.update(result__mirror_fields)
    return result


def handle_item(key, item, previous):
    from hdict.content.argument.entry import entry

    match item:
        case AbsEntry():
            res = item
        case field(name=name):
            if name not in previous:  # pragma: no cover
                raise MissingFieldException(f"Missing field `{name}`")
            res = handle_item(name, previous[name], previous)
        case entry(name=name):
            from hdict.content.entry.wrapper import Wrapper

            if name not in previous:  # pragma: no cover
                raise MissingFieldException(f"Missing entry `{name}`")
            res = Wrapper(handle_item(name, previous[name], previous))
        case apply():
            res = item.enclosure(previous, key)
        case sample():  # pragma: no cover
            raise Exception(f"Unsampled variable or argument `{key}`")
        case frozenhdict():
            res = value(item, item.hosh)
        case hdict():
            res = value(item.frozen, item.hosh)
        case ApplyOut():  # pragma: no cover
            raise Exception("Cannot assign output through both apply and dict-key: '>> {out: apply(...)(out)}'.")
        case AbsAny():  # pragma: no cover
            raise Exception(f"Cannot handle instance of type '{type(item).__name__}'.")
        case _ if str(type(item)) == "<class 'pandas.core.frame.DataFrame'>":
            from hdict.dataset.pandas_handling import explode_df

            res = explode_df(item)
        case _:
            res = value(item)

    if isinstance(key, tuple):
        return handle_multioutput(key, res, previous)
    elif not isinstance(key, str):  # pragma: no cover
        raise Exception(f"Invalid type for input field specification: {type(key).__name__}")
    elif key.startswith("_"):  # pragma: no cover
        raise Exception(f"Field names cannot start with '_': {key}")

    return res


def handle_identity(data):
    hosh = ø
    ids, later = {}, {}
    for k, v in data.items():
        # Handle meta. mirror, and field ids differently.
        if k.startswith("_"):  # pragma: no cover
            raise Exception("Custom metafields are not allowed:", k)
            # self.mhosh += self.data[k].hosh * k.encode()                # self.mids[k] = self.data[k].hosh.id
        elif k.endswith("_"):
            # mirrorfield, e.g.: 'df_' is a mirror/derived from 'df'
            later[k] = v.id
        else:
            hosh += v.hosh * k.encode()
            # PAPER REMINDER: state in the paper that hash(identifier) must be different from hash(value), for any identifier and value. E.g.: hash(X) != hash("X")    #   Here the difference always happen because values are pickled, while identifiers are just encoded().
            ids[k] = v.hosh.id
    ids.update(later)
    return hosh, ids


def handle_multioutput(field_names: tuple, entry: AbsEntry | apply, previous):
    """Fields and hoshes are assigned to each output according to the alphabetical order of the original keys.

    >>> from hdict import field, value
    >>> d = {"a": field("b"), "b": field("c"), "c": 5}
    >>> d
    {'a': field(b), 'b': field(c), 'c': 5}
    >>> handle_multioutput(("x","y"), value([0, 1]), d)
    {'x': 0, 'y': 1}
    >>> handle_multioutput(("x","y"), value({1: "a", 0: "b"}), d)
    {'x': 'b', 'y': 'a'}
    """
    from hdict import value
    from hdict.content.entry.subvalue import SubValue

    data = {}
    match entry:
        case value(value=list() as lst):
            if len(field_names) != len(lst):  # pragma: no cover
                raise Exception(f"Number of output fields ('{len(field_names)}') should match number of list elements ('{len(lst)}').")
            for field_name, val in zip(field_names, lst):
                data[field_name] = handle_item(field_name, val, previous)
        case value(value=dict() as dct):
            if len(field_names) != len(dct):  # pragma: no cover
                raise Exception(f"Number of output fields ('{len(field_names)}') should match number of dict entries ('{len(dct)}').")
            for field_name, (_, val) in zip(field_names, sorted(dct.items())):
                data[field_name] = handle_item(field_name, val, previous)
        case AbsEntry() | apply():
            keys = []  # For repr().
            parent = Closure(entry, previous, keys) if isinstance(entry, apply) else entry
            n = len(field_names)
            for key, i, source in loop_field_names(field_names):
                keys.append(key)
                data[key] = SubValue(parent, i, n, source)
        case _:  # pragma: no cover
            raise Exception(f"Cannot handle multioutput for key '{field_names}' and type '{type(entry).__name__}'.")
    return data


def loop_field_names(field_names):
    if all(isinstance(x, tuple) for x in field_names):
        source_target = sorted((sour, targ) for targ, sour in field_names)
        for i, sour_targ in enumerate(source_target):
            if len(sour_targ) != 2:  # pragma: no cover
                raise Exception(f"Output tuples should be string pairs 'target=source', not a sequence of length '{len(sour_targ)}'.", sour_targ)
            source, target = sour_targ
            yield target, i, source
    elif any(isinstance(x, tuple) for x in field_names):  # pragma: no cover
        raise Exception(f"Cannot mix translated and non translated outputs.", field_names)
    else:
        for i, field_name in enumerate(field_names):
            yield field_name, i, None


def handle_mirror(k, data, id, kind):  # object | Cached
    from hdict.content.entry.cached import Cached

    if not isinstance(data[k], (Cached, frozenhdict)):  # pragma: no cover
        raise Exception(f"Cannot handle fetched object of type `{type(data[k])}`")
    match kind:
        case "<class 'pandas.core.frame.DataFrame'>":
            f = lambda **kwargs: kwargs[k].asdf
            return apply(f, fhosh=ø, **{k: field(k)}).enclosure(data, k)
        case None:  # pragma: no cover
            pass
        case _:  # pragma: no cover
            raise Exception(f"Unknown mirror field kind `{kind}`.")


def handle_format(format, fields, df, name):
    """
    >>> from hdict import hdict
    >>> df = hdict(index=[1,2], X=[3,4], y=[5,6]).asdf
    >>> handle_format("Xy", ["X", "y"], df, True).show(colored=False)
    {
        X: "‹{'X': {1: 3, 2: 4}}›",
        y: "‹[0 1]›",
        name: true,
        _id: Qbcv80d7nEuKex05ecsNrCyQ4d7OI1XsgTWgcCcd,
        _ids: {
            X: oPj-WdtESlEAiUDqGQOUXR-4uwVNfYDl98o042.P,
            y: cm5S71YBRAlVWV5Yn9pXHzsacyZuEH4ZFDNAw9nu,
            name: oK8X-7eG1Qp1WH7v6fokBDrQPdngKn.h86tlEnx4
        }
    }
    >>> handle_format("df", ["X", "y"], df, True).show(colored=False)
    {
        df: "‹{'X': {1: 3, 2: 4}, 'y': {1: 5, 2: 6}}›",
        name: true,
        _id: Y8dS5prSxAflQwA0RvutZ.EMDRcyzeZAZCAAuWtT,
        _ids: {
            df: taqqcce8-I2nyIyk8LCm4iec0SVkrnbE6FjEvpiS,
            name: oK8X-7eG1Qp1WH7v6fokBDrQPdngKn.h86tlEnx4
        }
    }
    >>> handle_format("Xy", None, df, True).show(colored=False)
    {
        X: "‹{'X': {1: 3, 2: 4}}›",
        y: "‹[0 1]›",
        name: true,
        _id: Qbcv80d7nEuKex05ecsNrCyQ4d7OI1XsgTWgcCcd,
        _ids: {
            X: oPj-WdtESlEAiUDqGQOUXR-4uwVNfYDl98o042.P,
            y: cm5S71YBRAlVWV5Yn9pXHzsacyZuEH4ZFDNAw9nu,
            name: oK8X-7eG1Qp1WH7v6fokBDrQPdngKn.h86tlEnx4
        }
    }
    """
    if fields and not isinstance(fields, list):  # pragma: no cover
        raise Exception(f"`fields` must be a list.")
    if fields is None:
        fields = ["df"]
    if format == "df":
        if fields == ["X", "y"]:
            fields = ["df"]
        if len(fields) != 1:  # pragma: no cover
            raise Exception(f"Wrong number of fields {len(fields)}. Expected: 1.", fields)
        d = frozenhdict({fields[0]: df})
    elif format == "Xy":
        if fields == ["df"]:
            fields = ["X", "y"]
        if len(fields) != 2:  # pragma: no cover
            raise Exception(f"Wrong number of fields {len(fields)}. Expected: 2.", fields)
        dic = df2Xy(df=df)
        d = frozenhdict({fields[0]: dic["X"], fields[1]: dic["y"]})
    else:  # pragma: no cover
        raise Exception(f"Unknown {format=}.")

    if name:
        d >>= {"name": name}
    return d


# TODO:  fix apply() for *args
#
"""
            f = lambda *args: args[0].asdf
            return apply(f, field(k), fhosh=ø).enclosure(data, k)

        return apply(f, field(k), fhosh=ø).enclosure(data, k)
      File "/home/davi/git/hdict/src/hdict/content/argument/apply.py", line 311, in enclosure
        return Closure(self, data, [key])
      File "/home/davi/git/hdict/src/hdict/content/entry/closure.py", line 29, in __init__
        arg = handle_arg(key, val, data, discarded_defaults, out, self.torepr)
      File "/home/davi/git/hdict/src/hdict/content/entry/aux_closure.py", line 30, in handle_arg
        arg = handle_item(str(key), data[name], data)  # key passed for no purpose here AFAIR
      File "/home/davi/git/hdict/src/hdict/data/aux_frozendict.py", line 76, in handle_item
        raise Exception(f"Field names cannot start with '_': {key}")
    Exception: Field names cannot start with '_': _0

"""
