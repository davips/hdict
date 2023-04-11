from hosh import Hosh

from hdict.content.entry import AbsEntry, Unevaluated


class Cached(AbsEntry):
    """Layer to enable delaying fetching from storage"""

    def __init__(self, id: str, storage: dict, entry: AbsEntry = None):
        self.hosh = Hosh.fromid(id)
        self.storage = storage
        self.entry = entry

    @property
    def value(self):
        from hdict import frozenhdict
        if self._value == Unevaluated:
            if self.entry and self.entry.isevaluated:
                self._value = self.entry.value
            elif ret := frozenhdict.fetch(self.id, self.storage):
                self._value = ret
            elif self.entry is None:  # pragma: no cover
                raise Exception(f"id `{self.id}` not found.")
            else:
                from hdict.persistence.stored import Stored
                self._value = self.entry.value
                self.storage[self.id] = Stored(self._value)
        return self._value

    def __repr__(self):
        return f"↑↓ cached at `{type(self.storage).__name__}`·"
