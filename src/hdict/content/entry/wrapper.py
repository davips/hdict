from dataclasses import dataclass

from hdict.content.entry import AbsEntry, Unevaluated


@dataclass
class Wrapper(AbsEntry):
    entry: AbsEntry

    def __post_init__(self):
        self.hosh = self.entry.hosh

    @property
    def value(self):
        if self._value is Unevaluated:
            self._value = self.entry
        return self._value

    def __repr__(self):
        return repr(self.entry)
