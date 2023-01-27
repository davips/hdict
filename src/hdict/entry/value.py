from hdict.entry.abscontent import AbsContent
from hdict.hoshfication import v2hosh
from hosh import Hosh


class value(AbsContent):
    """
    >>> x = 5
    >>> from hdict import value
    >>> v = value(x)
    >>> v.value
    5
    >>> v
    5

    """

    def __init__(self, value: object, hosh: Hosh = None, hdict=None):
        """

        Args:
            value:
            hosh:
            hdict:  optional reference to the object if it has a hdict counterpart (e.g.: pandas DF)
        """
        if isinstance(value, AbsContent):
            raise Exception(f"Cannot nest AbsContent object inside a 'value' object: '{type(value)}")
        self.value = value
        self._hosh = Hosh.fromid(hosh) if isinstance(hosh, str) else hosh
        self.hdict = hdict
        self.isevaluated = True

    @property
    def hosh(self):
        return v2hosh(value) if self._hosh is None else self._hosh

    def __repr__(self):
        return repr(self.value)

#  d["z"] = apply(f, 2, y=3)
#  d["w", "v"] = apply(f, field("x"), y=field("y"))
#  d["w", "v"] = apply(field("f"), field("x"), y=default(3))
#  d = hdict() >> {"z": apply(f, field("x"), y=3), ("w", "v"): apply(g, y=7)}
#  d = hdict() >> apply(f, field("x"), y=3)("z") >> apply(g, y=7)("w", "v")
#  p = apply(f, y=_[1, 2, 4, ..., 128])("z") * apply(f, y=_[0, 3, 6, ..., 9])(w="a", v="b")
#  d = p.sample(rnd)

#  d["z"] = _(f, 2, y=3)
#  d["w", "v"] = _(f, _.x, y=_.y)
#  d["w", "v"] = _(_.f, _.x), y=default(3))
#  d = hdict() >> {"z": _(f, _.x, y=3), ("w", "v"): _(g, y=7)}
#  d = hdict() >> _(f, _.x, y=3)("z") >> _(g, y=7)("w", "v")
#  p = _(f, y=_[1, 2, 4, ..., 128])("z") * _(f, y=_[0, 3, 6, ..., 9])(w="a", v="b")
#  d = p.sample(rnd)
