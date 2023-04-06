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
from hdict.aux_frozendict import handle_items, prevent_overwriting_unready
from hdict.content.argument.apply import apply
from hdict.content.entry.ready import AbsReadyEntry
from hdict.content.entry.ready.closure import Closure


def handle_multioutput(result, field_names: tuple, entry: AbsReadyEntry, ignore):
    """Fields and hoshes are assigned to each output according to the alphabetical order of the original keys.

    >>> from hdict import field, value
    >>> d = {"a": field("b"), "b": field("c"), "c": 5}
    >>> d
    {'a': 'b', 'b': 'c', 'c': 5}
    >>> handle_multioutput(d, ("x","y"), value([0,1]))
    ({'a': 'b', 'b': 'c', 'c': 5, 'x': 0, 'y': 1}, False, False)
    >>> d
    {'a': 'b', 'b': 'c', 'c': 5, 'x': 0, 'y': 1}
    >>> handle_multioutput(d, ("x","y"), value({1:"a", 0:"b"}))
    ({'a': 'b', 'b': 'c', 'c': 5, 'x': 'b', 'y': 'a'}, False, False)
    >>> d
    {'a': 'b', 'b': 'c', 'c': 5, 'x': 'b', 'y': 'a'}
    """
    from hdict import value
    from hdict.content.entry.ready.subvalue import SubValue
    data = {}
    match entry:
        case value(value=list() as lst):
            if len(field_names) != len(lst):  # pragma: no cover
                raise Exception(f"Number of output fields ('{len(field_names)}') should match number of list elements ('{len(lst)}').")
            for field_name, val in zip(field_names, lst):
                data[field_name] = val
            return handle_items(data, result=result, ignore=ignore)
        case value(value=dict() as dct):
            if len(field_names) != len(dct):  # pragma: no cover
                raise Exception(f"Number of output fields ('{len(field_names)}') should match number of dict entries ('{len(dct)}').")
            for field_name, (_, val) in zip(field_names, sorted(dct.items())):
                data[field_name] = val
            return handle_items(data, result=result, ignore=ignore)
        case AbsReadyEntry():
            parent = Closure(entry, result, ignore) if isinstance(entry, apply) else entry
            n = len(field_names)
            for key, i, source in loop_field_names(field_names):
                prevent_overwriting_unready(key, SubValue(parent, i, n, source), result, ignore)
            return result, False, False
        case _:  # pragma: no cover
            raise Exception(f"Cannot handle multioutput for key '{field_names}' and type '{entry.__class__.__name__}'.")


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
