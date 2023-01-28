from dataclasses import dataclass

from hdict.entry.abscontent import AbsContent
from hdict.entry.apply import apply


@dataclass
class applyOut(AbsContent):
    apply: apply
    out: [str]

    def __post_init__(self):
        self.f = self.apply.f
        self.fun = self.apply.fun
        self.fhosh = self.apply.fhosh
        self.ahosh = self.apply.ahosh
        self.args = self.apply.args
        self.kwargs = self.apply.kwargs
        self.requirements = self.apply.requirements
        # noinspection PyTypeChecker
        self.hosh = self.apply.hosh
        self.fun = self.apply.fun
        self.isevaluated = self.apply.isevaluated
        self.value = self.apply.evaluate
        self.__repr__ = self.apply.__repr__
