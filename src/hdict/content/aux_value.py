#  Copyright (c) 2023. Davi Pereira dos Santos
#  This file is part of the hdict project.
#  Please respect the license - more about this in the section (*) below.
#
#  hdict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  hdict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with hdict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#

import dis
import re
from collections import OrderedDict
from inspect import signature, isbuiltin, isclass
from pickle import dumps

from hosh import Hosh, ø


def v2hosh(value: object) -> Hosh:
    """
    Convert any value to a hosh object.

    `value` should be serializable (by pickle).
    Adopt pickle for hoshfication because it is faster.

    >>> obj = {"x": 3, "l": [1, 2, "5"]}
    >>> print(v2hosh(obj))
    z0cJsCBPY7cHt.oJnrpyk23FOlPdCcYvcX8x7jg6
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
            if callable(value):
                return f2hosh(value)
            # REMINDER: pickle is the fastest serialization
            return Hosh(dumps(value, protocol=5))
        except TypeError as e:  # pragma: no cover
            if "disassemble _PredictScorer" in str(e) or "disassemble _ProbaScorer" in str(e):
                return Hosh(dumps(value, protocol=5))
            raise Exception(f"Cannot pickle. Pickling is needed to hosh hdict values ({value}): {e}")


def f2hosh(function: callable):
    """
    Convert a function to a hosh object.

    Adopt pickle(bytecode) for hoshfication because it is faster than other serializations of bytecode.

    >>> fun = lambda x, y: x + y
    >>> print(f2hosh(fun))
    vD8.I-NU3x5hzmj-m1EJgeAIE-.H.HGnWxqvZng0
    >>> fun.hosh = ø * "My-custom-identifier-arbitrarily-defined"
    >>> print(f2hosh(fun))
    My-custom-identifier-arbitrarily-defined
    """
    if hasattr(function, "hosh"):
        return function.hosh
    if isbuiltin(function) or isclass(function):
        return Hosh(str(function).encode())
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
    # REMINDER: pickle chosen because it is the fastest serialization (see bottom of the file)
    return Hosh(dumps(code, protocol=5))


# Timing:
"""
l = [{"x": 3}, 530934590.435903475, "4p9fj24gifh2430g8h230g82h34g0p2843hg02h"] * 100


def f():
    pack(l, ensure_determinism=True, unsafe_fallback=False, compressed=False)


def g():
    dumps(l)


def h():
    pack(l, ensure_determinism=True, unsafe_fallback=False, compressed=True)


print(timeit(f, number=1000))
print(timeit(g, number=1000))
print(timeit(h, number=1000))
"""
