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


def handle_field(name, result):
    if name not in result:
        raise MissingFieldException(name)
    return result[name]


def handle_default(key, val, result):
    from hdict.content.value import value
    from hdict.content.field import field
    if key in result:
        # 'default' unneeded.
        return result[key]
    elif isinstance(val.value, field):
        return handle_field(val.value.name, result)
    elif isinstance(val.value, value):
        return val.value
    else:  # TODO: 'object' ?
        raise Exception(f"Unhandled type for default value: '{type(val)}.{type(val.value)}'")


def handle_applied_arg(key, val, result):
    from hdict.content.value import value
    from hdict.content.field import field
    from hdict import default
    if isinstance(val, default):
        return handle_default(key, val, result)
    elif isinstance(val, field):
        return handle_field(val.name, result)
    elif isinstance(val, value):
        if isinstance(val.value, field):
            raise Exception(f"")  # TODO: useless excep?
        return val
    else:
        print(val)
        print(val.value.name)
        raise Exception(f"Unhandled type as requirement: '{type(val)}.{type(val.value)}'")


def handle_values(*datas: [Dict[str, object]]):
    from hdict import hdict
    from hdict.content.value import value
    from hdict.content.field import field
    from hdict import default
    from hdict.content.closure import Closure
    from hdict.content.abs.sampling import withSampling
    from hdict.content.applyout import applyOut
    from hdict.content.handling import handle_multioutput
    from hdict.content.abs.appliable import AbsAppliable
    from hdict.content.handling import check_dup

    result, unfinished, result__mirror_fields, subcontent_cloned_parent = {}, {}, {}, {}
    for k, content in chain(*(data.items() for data in datas)):
        check_dup(k, result)
        if isinstance(content, withSampling) and content.sampleable:
            raise UnsampledException(k, type(content))

        if isinstance(k, tuple):
            if isinstance(content, field):
                content = handle_field(content.name, result)
            handle_multioutput(result, k, content)
            continue
        elif not isinstance(k, str):  # pragma: no cover
            raise Exception(f"Invalid type for input field specification: {type(k)}")

        if isinstance(content, value):
            result[k] = content
        elif isinstance(content, field):
            result[k] = handle_field(content.name, result)
        elif isinstance(content, default):  # pragma: no cover
            raise Exception(f"Cannot pass object of type 'default' directly to hdict. Param:", k)
        elif isinstance(content, AbsAppliable):
            result[k] = Closure(content, result)
        elif isinstance(content, hdict):
            result[k] = value(content.frozen, content.hosh)
        elif str(type(content)) == "<class 'pandas.core.frame.DataFrame'>":
            result[k] = val = explode_df(content)
            if k.endswith("_"):
                result__mirror_fields[f"{k[:-1]}"] = value(val.hdict, val.hosh)
        elif isinstance(content, applyOut):  # pragma: no cover
            raise Exception("Cannot assign output through both apply and dict-key: '>> {out: apply(...)(out)}'.")
        elif isinstance(content, AbsAny):  # pragma: no cover
            raise Exception(f"Cannot handle instance of type '{type(content)}'.")
        else:
            result[k] = value(content)

        if k.startswith("_"):  # pragma: no cover
            raise Exception(f"Field names cannot start with '_': {k}")

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
