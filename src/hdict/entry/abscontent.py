from abc import ABC

from hosh import Hosh


class Undefined:
    pass


Undefined = Undefined()


class AbsContent(ABC):
    value: object
    hosh: Hosh
    isevaluated: bool

    @property
    def id(self):  # pragma: no cover
        return self.hosh.id

    def evaluate(self):
        _ = self.value
