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
from dataclasses import dataclass

from hdict.abs import AbsAny


@dataclass
class Cache(AbsAny):
    storage: dict

    def __rrshift__(self, left):
        from hdict import hdict, frozenhdict
        match left:
            case hdict() | frozenhdict():
                fields = (field for field, entry in left.raw.items() if not entry.isevaluated)
                return left >> cache(self.storage, *fields)
        return NotImplemented


def cache(storage: dict, /, *fields):
    """
    >>> from hdict import _, hdict, cache, apply
    >>> storage = {}
    >>> d = hdict(x=3, y=5) >> apply(lambda x, y: x / y).z
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        z: λ(x y),
        _id: UB8No.x9HiKWeFqpmTv1lWn0lEsTJS16lPNCojcK,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: cszQVZnzMQSS3.2tdWWQL-wGCv.lO0TWqVoSNFww
        }
    }
    >>> d >>= cache(storage)
    >>> d.show(colored=False)
    >>> d.evaluate()
    >>> d.show(colored=False)
    {
        x: 3,
        y: 5,
        z: 0.6,
        _id: bSXTaET8cR-V6f9Zaf1K3fIS6yYIWJhF6DgQ.At7,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            z: XFTNm3npQiPmV4uZ4-lX8IIUWgbHW-6uc5n3pXNV
        }
    }
    >>>
    """
    if not fields:
        return Cache(storage)
    from hdict.content.argument.apply import apply
    from hdict.content.argument.entry import entry
    def f(**kwargs):
        return [storage[key] if key in storage else entry.value for key, entry in kwargs.items()]

    return {fields: apply(f, **{k: entry(k) for k in fields})}


@dataclass
class Cached(AbsAny):
    content: object
