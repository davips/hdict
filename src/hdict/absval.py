from hosh import Hosh


class AbsVal:
    value: object
    hosh: Hosh
    isevaluated: bool

    @property
    def id(self):  # pragma: no cover
        return self.hosh.id
