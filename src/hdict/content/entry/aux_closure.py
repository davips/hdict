from __future__ import annotations

from hdict.content.argument import AbsBaseArgument


def handle_arg(key, val, data, discarded_defaults, out, torepr, previous):
    """Return handled arg and value of pseudocircular entry"""
    from hdict.content.argument.default import default
    from hdict.content.value import value
    from hdict.data.aux_frozendict import handle_item
    from hdict import field
    from hdict.data.aux_frozendict import MissingFieldException

    from hdict.content.argument.entry import entry

    if key == "_":
        return handle_item(key, previous, data, previous)
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
            if name not in data:  # pragma: no cover
                raise MissingFieldException(f"Missing pseudocircular field `{name}`")
            arg = handle_item(str(key), data[name], data, previous)  # key passed for no purpose here AFAIR
            torepr[key] = arg
            return arg
        case entry(name=name):
            from hdict.content.entry.wrapper import Wrapper

            if name not in data:  # pragma: no cover
                raise MissingFieldException(f"Missing pseudocircular field `{name}`")
            content = handle_item(str(key), data[name], data, previous)
            arg = Wrapper(content)
            torepr[f"·{name}"] = arg
            return arg
        case AbsBaseArgument():
            arg = handle_item(str(key), val, data, previous)
        case _:  # pragma: no cover
            raise Exception(f"Cannot handle argument of type `{type(val).__name__}`")
    torepr[key] = val
    return arg
