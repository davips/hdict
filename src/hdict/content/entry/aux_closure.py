from __future__ import annotations

from hdict.aux_frozendict import MissingFieldException
from hdict.content.argument import AbsBaseArgument


def handle_arg(key, val, data, discarded_defaults, out, torepr):
    """Return handled arg and value of pseudocircular entry"""
    from hdict.content.argument.default import default
    from hdict.content.value import value
    from hdict.aux_frozendict import handle_item
    from hdict import field

    match val:
        case default(value=v):
            if key in data:
                arg = data[key]
                # REMINDER: `discarded_defaults` exists only for __repr__ purposes
                discarded_defaults.add(key)
            else:
                arg = value(v)
            if key in out:
                torepr[key] = arg
                return arg
        case field(name=name) if name in out:  # Override case of handle_item if pseudocircular reference.
            if name not in data:
                raise MissingFieldException(f"Missing pseudocircular field `{name}`")
            arg = handle_item(str(key), val, data)
            torepr[key] = arg
            return arg
        case AbsBaseArgument():
            arg = handle_item(str(key), val, data)
        case _:
            raise Exception(f"Cannot handle argument of type `{type(val).__name__}`")
    torepr[key] = val
    return arg


def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
