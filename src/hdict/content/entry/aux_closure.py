from __future__ import annotations

from hdict.content.argument import AbsBaseArgument
from hdict.content.entry.unready import AbsUnreadyEntry


def handle_arg(key, val, result, discarded_defaults, ignore):
    from hdict.content.argument.default import default
    from hdict.content.value import value
    from hdict.aux_frozendict import handle_item
    match val:
        case default(value=v):
            if key in result:
                arg = result[key]
                # REMINDER: `discarded_defaults` exists only for __repr__ purposes
                discarded_defaults.add(key)
            else:
                arg = value(v)
        case AbsBaseArgument():
            arg = handle_item(val, result, ignore)
        case _:
            raise Exception(f"Cannot handle argument of type `{val.__class__.__name__}`")
    if isinstance(arg, AbsUnreadyEntry):
        return None
    return arg
