import dis
import re
from collections import OrderedDict
from inspect import signature

from hosh import Hosh, ø
from lazydf.compression import pack


def v2hosh(value: object) -> Hosh:
    """
    Convert any value to a hosh object.

    `value` should be serializable (by json or pickle).

    >>> obj = {"x": 3, "l": [1, 2, "5"]}
    >>> print(v2hosh(obj))
    f1mPuinEzcp7qvmsmpahVnTYo1cg6VtHi4GnKF4j
    >>> # We encapsulate 'obj' as built-in types cannot be easily patched.
    >>> obj = OrderedDict(obj)
    >>> obj.hosh = ø * "My-custom-identifier-arbitrarily-defined"
    >>> print(v2hosh(obj))
    My-custom-identifier-arbitrarily-defined
    """
    if hasattr(value, "hosh"):
        return value.hosh
    else:
        try:
            return Hosh(pack(value, ensure_determinism=True, unsafe_fallback=False, compressed=False))
        except TypeError as e:  # pragma: no cover
            raise Exception(f"Cannot pickle. Pickling is needed to hosh idict values ({value}): {e}")


def f2hosh(function: callable):
    """
    Convert a function to a hosh object.

    >>> fun = lambda x, y: x + y
    >>> print(f2hosh(fun))
    RMsMxUaW5VqKBN0-V1Q6obDEvZTkeR3oKjhoR.U1
    >>> fun.hosh = ø * "My-custom-identifier-arbitrarily-defined"
    >>> print(f2hosh(fun))
    My-custom-identifier-arbitrarily-defined
    """
    if hasattr(function, "hosh"):
        return function.hosh
    fields_and_params = signature(function).parameters.values()
    fields_and_params = {v.name: None if v.default is v.empty else v.default for v in fields_and_params}

    # Remove line numbers.
    groups = [l for l in dis.Bytecode(function).dis().split("\n\n") if l]
    clean_lines = [fields_and_params]

    for group in groups:
        # Replace memory addresses and file names by just the object name.
        group = re.sub(r'<code object (.+) at 0x[0-f]+, file ".+", line \d+>', r"\1", group)
        lines = [re.sub(r"^[\d ]+", "", segment) for segment in re.split(" +", group)][1:]
        clean_lines.append(lines)
    code = [fields_and_params, clean_lines]
    return Hosh(pack(code, ensure_determinism=True, unsafe_fallback=False, compressed=False))
