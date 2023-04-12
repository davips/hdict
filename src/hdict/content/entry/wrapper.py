from dataclasses import dataclass

from hdict.content.entry import AbsEntry, Unevaluated


@dataclass
class Wrapper(AbsEntry):
    """
    The only entry that can nest and return another entry as a value

    For advanced usage only
    """

    entry: AbsEntry

    def __post_init__(self):
        self.hosh = self.entry.hosh

    @property
    def value(self):
        if isinstance(self._value, Unevaluated):
            self._value = self.entry
        return self._value

    def __repr__(self):
        return "·" + repr(self.entry)
