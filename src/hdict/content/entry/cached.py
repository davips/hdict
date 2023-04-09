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
        if self._value is Unevaluated:
            if self.entry.isevaluated:
                self._value = self.entry.value
            elif self.id in self.storage:
                from hdict import frozenhdict
                self._value = frozenhdict.fetch(self.id, self.storage).content
            elif self.entry is None:
                raise Exception(f"id `{self.id}` not found.")
            else:
                self._value = self.entry.value
                self.storage[self.id] = self._value
        return self._value

    def __repr__(self):
        return f"§«§lazy«lazy value at cache `{type(self.storage).__name__}`»lazy§«§"  # TODO: solve the unquotation by regex
