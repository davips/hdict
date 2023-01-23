from hosh import Hosh


class AbsArg:
    value: object
    hosh: Hosh
    isevaluated: bool
    ispositional:bool

    @property
    def id(self):  # pragma: no cover
        return self.hosh.id
