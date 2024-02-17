from itertools import chain
from typing import Dict
from typing import TypeVar

from hosh import ø, Hosh

from hdict import hdict, value, frozenhdict, Self
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


def handle_items(*datas: [Dict[str, object]], previous: frozenhdict):
    result = {} if previous is None else previous.raw.copy()
    result__mirror_fields = {}
    for key, item in chain(*(data.items() for data in datas)):
        entry = handle_item(key, item, result, previous)
        if isinstance(key, str) and key.endswith("_") and not key.startswith("_"):
            if isinstance(entry, value):
                result__mirror_fields[f"{key[:-1]}"] = value(entry.hdict, entry.hdict.hosh)
            else:
                raise Exception(f"lazy mirror?")  # todo:
        if isinstance(entry, dict):
            result.update(entry)
        else:
            result[key] = entry
    result.update(result__mirror_fields)
    return result


def handle_item(key, item, result, previous):
    from hdict.content.argument.entry import entry

    match item:
        case AbsEntry():
            res = item
        case field(name=name):
            if name not in result:  # pragma: no cover
                raise MissingFieldException(f"Missing field `{name}`")
            res = handle_item(name, result[name], result, previous)
        case entry(name=name):
            from hdict.content.entry.wrapper import Wrapper

            if name not in result:  # pragma: no cover
                raise MissingFieldException(f"Missing entry `{name}`")
            res = Wrapper(handle_item(name, result[name], result, previous))
        case apply():
            res = item.enclosure(result, key, previous)
        case sample():  # pragma: no cover
            raise Exception(f"Unsampled variable or argument `{key}`")
        case frozenhdict():
            res = value(item, item.hosh)
        case hdict():
            res = value(item.frozen, item.hosh)
        case ApplyOut():  # pragma: no cover
            raise Exception("Cannot assign output through both apply and dict-key: '>> {out: apply(...)(out)}'.")
        case Self():
            if previous is None:
                raise Exception(f"Cannot reference self in a new hdict. `_` is intended to point to a hdict before application.")
            res = handle_item(key, previous, result, None)
        case AbsAny():  # pragma: no cover
            raise Exception(f"Cannot handle instance of type '{type(item).__name__}'.")
        case _ if str(type(item)) == "<class 'pandas.core.frame.DataFrame'>":
            from hdict.dataset.pandas_handling import explode_df

            # todo: check if this is the best default way of handling DFs.
            df = item.copy(deep=False)
            d = explode_df(df)
            df.__dict__["ashdict"] = d
            res = value(df, hosh=d.hosh.rev, hdict=d)
        case _:
            res = value(item)

    if isinstance(key, tuple):
        return handle_multioutput(key, res, result, previous)
    elif not isinstance(key, str):  # pragma: no cover
        raise Exception(f"Invalid type for input field specification: {type(key).__name__}")
    # reminder: some parameter names start with: `__o` in getattr(__o)

    return res


def handle_identity(data):
    """
    >>> from hdict import _
    >>> d = hdict(_x_=5)
    >>> d.show(colored=False)
    {
        _x_: 5,
        _id: 0000000000000000000000000000000000000000,
        _ids: {
            _x_: "bwXY2nkgcPxh5U9ccraq-iznyWbzNYNQDp4HzejJ"
        }
    }
    >>> d.apply(lambda x: x**2, x=_._x_, out="r")
    >>> d.evaluated.show(colored=False)
    {
        _x_: 5,
        r: 25,
        _id: 9iw-s44RA7bJPi5sIejt2i1HHq2WB2uUTBOWc5-u,
        _ids: {
            r: 5E5iUv0J2e.GePNtAn6ley68v9nei9Sy5v4gfO2a,
            _x_: "bwXY2nkgcPxh5U9ccraq-iznyWbzNYNQDp4HzejJ"
        }
    }
    >>> (Hosh.fromid("9iw-s44RA7bJPi5sIejt2i1HHq2WB2uUTBOWc5-u")-("5E5iUv0J2e.GePNtAn6ley68v9nei9Sy5v4gfO2a"*Hosh(b"r"))).id
    '0000000000000000000000000000000000000000'
    >>> (Hosh.fromid("0000000000000000000000000000000000000000") / Hosh(b"_x_")).id
    'bwXY2nkgcPxh5U9ccraq-iznyWbzNYNQDp4HzejJ'
    """
    hosh = ø
    ids, later = {}, {}
    for k, v in data.items():
        # Handle meta,mirror field ids differently. e.g.: 'df_' is a mirror/derived from 'df'
        if k[-1] == "_":
            if k[0] == "_":
                if len(k) < 3:
                    raise Exception(f"Cannot have a field named `__`.")
                v = value(v.value, hosh=~Hosh(k.encode()))  # metafield, e.g.: "_myfield_"
            later[k] = v.id
        else:
            ids[k] = v.hosh.id
        hosh += v.hosh * k.encode()
        # todo:  PAPER REMINDER: state in the paper that identifiers are not strings. they are a special type that never appears as a value.
        #   I.e., hash(identifier) must be different from hash(value), for all identifiers and values.
        #   E.g.: hash(field name X) != hash(string "X")
        #   In this impementation, the difference is always* true because values are always pickled (they are never hashed as strings), while identifiers are just str.encoded().
        #   * → probabilistically
    ids.update(later)
    return hosh, ids


def handle_multioutput(field_names: tuple, entry: AbsEntry | apply, previous_result, previous):
    """Fields and hoshes are assigned to each output according to the alphabetical order of the original keys.

    >>> from hdict import field, value
    >>> d = {"a": field("b"), "b": field("c"), "c": 5}
    >>> d
    {'a': field(b), 'b': field(c), 'c': 5}
    >>> handle_multioutput(("x","y"), value([0, 1]), d, None)
    {'x': 0, 'y': 1}
    >>> handle_multioutput(("x","y"), value({1: "a", 0: "b"}), d, None)
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
                data[field_name] = handle_item(field_name, val, previous_result, previous)
        case value(value=dict() as dct):
            if len(field_names) != len(dct):  # pragma: no cover
                raise Exception(f"Number of output fields ('{len(field_names)}') should match number of dict entries ('{len(dct)}').")
            for field_name, (_, val) in zip(field_names, sorted(dct.items())):
                data[field_name] = handle_item(field_name, val, previous_result, previous)
        case AbsEntry() | apply():
            keys = []  # For repr().
            parent = Closure(entry, previous_result, keys, previous) if isinstance(entry, apply) else entry
            n = len(field_names)
            for key, i, source in loop_field_names(field_names):
                if key is not None:
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


# def handle_mirror(k, data, id, kind, previous):  # object | Cached
#     from hdict.content.entry.cached import Cached
#
#     if not isinstance(data[k], (Cached, frozenhdict)):  # pragma: no cover
#         raise Exception(f"Cannot handle fetched object of type `{type(data[k])}`")
#     match kind:
#         case "<class 'pandas.core.frame.DataFrame'>":
#             f = lambda **kwargs: kwargs[k].asdf
#             return apply(f, fhosh=ø, **{k: field(k)}).enclosure(data, k, previous)
#         case None:  # pragma: no cover
#             pass
#         case _:  # pragma: no cover
#             raise Exception(f"Unknown mirror field kind `{kind}`.")


def handle_format(format, fields, df, name):
    """
    >>> from hdict import hdict
    >>> df = hdict(index=[1,2], X=[3,4], y=[5,6]).asdf
    >>> handle_format("Xy", ["X", "y"], df, True).show(colored=False)
    {
        X: "‹{'X': {1: 3, 2: 4}}›",
        y: "‹[0 1]›",
        name: true,
        _id: rd.NmqV3FPKd3o5c7XAcPcJ6GFkK7O5XSAZR7JkV,
        _ids: {
            X: OMVTYSyh4Tl7V-eDNkbZ.1j79E5eLBOPLtXB.87w,
            y: cm5S71YBRAlVWV5Yn9pXHzsacyZuEH4ZFDNAw9nu,
            name: oK8X-7eG1Qp1WH7v6fokBDrQPdngKn.h86tlEnx4
        }
    }
    >>> handle_format("df", ["X", "y"], df, True).show(colored=False)
    {
        df: "‹{'X': {1: 3, 2: 4}, 'y': {1: 5, 2: 6}}›",
        name: true,
        _id: VWDHscqLlIW-Fu6bOAjrEBHzUehukqBOxK3RM4m9,
        _ids: {
            df: wTtDSUgXcZQVqx-CBZI-L9h4zVjAazPRGQOUNza8,
            name: oK8X-7eG1Qp1WH7v6fokBDrQPdngKn.h86tlEnx4
        }
    }
    >>> handle_format("Xy", None, df, True).show(colored=False)
    {
        X: "‹{'X': {1: 3, 2: 4}}›",
        y: "‹[0 1]›",
        name: true,
        _id: rd.NmqV3FPKd3o5c7XAcPcJ6GFkK7O5XSAZR7JkV,
        _ids: {
            X: OMVTYSyh4Tl7V-eDNkbZ.1j79E5eLBOPLtXB.87w,
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
