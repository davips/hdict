from dataclasses import dataclass

from hosh import Hosh

from hdict.absval import AbsVal
from hdict.hoshfication import v2hosh, f2hosh


class StrictVal(AbsVal):
    """
    >>> x = 5
    >>> from hdict.strictval import StrictVal
    >>> v = StrictVal(x)
    >>> v.value
    5
    >>> v
    5

    """

    def __init__(self, value: object, hosh: Hosh = None, hdict=None):
        self.value = value
        self.hosh = v2hosh(value) if hosh is None else hosh
        self.hdict = hdict
        self.isevaluated = True

    def __repr__(self):
        return repr(self.value)
