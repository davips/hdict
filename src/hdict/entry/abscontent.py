from hosh import Hosh


class AbsContent:
    value: object
    hosh: Hosh
    isevaluated: bool

    @property
    def id(self):  # pragma: no cover
        return self.hosh.id
