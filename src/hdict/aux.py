from functools import reduce
from itertools import chain
from operator import rshift
from typing import Dict
from typing import TypeVar

from hdict.content import MissingFieldException, UnsampledException
from hdict.content.abs.any import AbsAny
from hdict.pandas_handling import explode_df
from hdict.pipeline import pipeline

VT = TypeVar("VT")


def traverse_field(content, result):
    from hdict import field
    while isinstance(content, field):
        name = content.name
        if name not in result:
            raise MissingFieldException(name)
        content = result[name]
    return content


def handle_default(key, defv, result):
    from hdict.content.value import value
    if key in result:
        return traverse_field(result[key], result)
    content = traverse_field(defv.value, result)
    if isinstance(content, value):
        return content
    else:  # TODO: 'object' ?
        raise Exception(f"Unhandled type for default value: '{type(defv)}.{type(defv.value)}'")


def handle_applied_arg(key, val, result):
    from hdict.content.value import value
    from hdict.content.field import field
    from hdict import default
    content = traverse_field(val, result)
    if isinstance(content, default):
        return handle_default(key, content, result)
    elif isinstance(content, value):
        if isinstance(content.value, field):
            raise Exception(f"")  # TODO: useless excep?
        return content
    else:
        print(content)
        print(content.value.name)
        raise Exception(f"Unhandled type as requirement: '{type(content)}.{type(content.value)}'")


def handle_values(*datas: [Dict[str, object]]):
    from hdict import hdict
    from hdict.content.value import value
    from hdict import default
    from hdict.content.closure import Closure
    from hdict.content.abs.sampling import withSampling
    from hdict.content.applyout import applyOut
    from hdict.content.handling import handle_multioutput
    from hdict.content.abs.appliable import AbsAppliable
    from hdict.content.handling import create_entry

    result, unfinished, result__mirror_fields, subcontent_cloned_parent = {}, {}, {}, {}
    for k, content in chain(*(data.items() for data in datas)):
        if isinstance(content, withSampling) and content.sampleable:
            raise UnsampledException(k, type(content))

        content = traverse_field(content, result)

        if isinstance(k, tuple):
            handle_multioutput(result, k, content)
            res=None
        elif not isinstance(k, str):  # pragma: no cover
            raise Exception(f"Invalid type for input field specification: {type(k)}")

        elif isinstance(content, value):
            res = content
        elif isinstance(content, default):  # pragma: no cover
            raise Exception(f"Cannot pass object of type 'default' directly to hdict. Param:", k)
        elif isinstance(content, AbsAppliable):
            res = Closure(content, result)
        elif isinstance(content, hdict):
            res = value(content.frozen, content.hosh)
        elif str(type(content)) == "<class 'pandas.core.frame.DataFrame'>":
            res = val = explode_df(content)
            if k.endswith("_"):
                result__mirror_fields[f"{k[:-1]}"] = value(val.hdict, val.hosh)
        elif isinstance(content, applyOut):  # pragma: no cover
            raise Exception("Cannot assign output through both apply and dict-key: '>> {out: apply(...)(out)}'.")
        elif isinstance(content, AbsAny):  # pragma: no cover
            raise Exception(f"Cannot handle instance of type '{type(content)}'.")
        else:
            res = value(content)

        if k.startswith("_"):  # pragma: no cover
            raise Exception(f"Field names cannot start with '_': {k}")
        if res is not None:
            create_entry(k, result, res)

    # Mirror fields should appear at the end of hdict.
    result.update(result__mirror_fields)
    return result


def handle_rshift(self, other):
    from hdict.frozenhdict import frozenhdict
    from hdict import hdict
    from hdict.content.applyout import applyOut

    if isinstance(other, pipeline):
        return reduce(rshift, chain([self], other))

    # Merge keeping ids.
    if isinstance(other, hdict):
        other = other.frozen
    if isinstance(other, frozenhdict):
        other = other.data
    if isinstance(other, applyOut):
        other = {other.out: other.nested}

    data: dict[str, object] = self.data.copy()
    if isinstance(other, dict):  # merge keeping ids of AbsEntry objects if any is present
        data.update(other)
        return frozenhdict(data)
    return NotImplemented  # pragma: no cover
