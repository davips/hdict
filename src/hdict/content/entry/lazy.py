from hosh import Hosh

from hdict.content.entry import AbsEntry, Unevaluated


class Lazy(AbsEntry):
    def __init__(self, id: str, cache: dict):
        self.hosh = Hosh.fromid(id)
        self.cache = cache

    @property
    def value(self):
        if self._value is Unevaluated:
            self._value = self.cache[self.id]
        return self._value

    def __repr__(self):
        return f"§«§lazy«lazy value at cache `{type(self.cache).__name__}`»lazy§«§"  # TODO: solve the unquotation by regex
