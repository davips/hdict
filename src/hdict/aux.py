from functools import reduce
from itertools import chain
from operator import rshift
from typing import TypeVar

from hdict.pipeline import pipeline

VT = TypeVar("VT")


def handle_rshift(self, other):
    from hdict.frozenhdict import frozenhdict
    from hdict import hdict
    from hdict.content.applyout import applyOut

    if isinstance(other, pipeline):
        return reduce(rshift, chain([self], other))
    data: dict[str, object] = self.data.copy()
    if isinstance(other, hdict):  # merge keeping ids
        other = other.frozen
    if isinstance(other, frozenhdict):  # merge keeping ids
        other = other.data
    if isinstance(other, applyOut):
        other = {other.out: other.nested}
    if isinstance(other, dict):  # merge keeping ids of AbsContent objects if any is present
        for k, v in other.items():
            if isinstance(v, applyOut):  # pragma: no cover
                raise Exception("Cannot assign output through both apply and dict-key: '>> {out: apply(...)(out)}'.")
            if isinstance(k, tuple):
                from hdict.content.handling import handle_multioutput

                handle_multioutput(data, k, v)
            elif isinstance(k, str):
                data[k] = v
            else:  # pragma: no cover
                raise Exception(f"Invalid type for input field specification: {type(k)}")
        del data["_id"]
        del data["_ids"]
        return frozenhdict(data, _previous=self.data)
    return NotImplemented  # pragma: no cover
