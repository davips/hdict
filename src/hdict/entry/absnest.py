from functools import cached_property

from hdict.entry import Unfilled
from hdict.entry.abscontent import AbsContent


class AbsNest(AbsContent):
    _content: AbsContent = None

    @property
    def value(self):
        return self.content.value

    @property
    def iscloned(self):
        return self._content == Unfilled

    @property
    def isfilled(self):
        return self._content not in [None, Unfilled]

    @cached_property
    def content(self):
        if not self.isfilled:
            raise Exception(f"Cannot access content before cloning and filling pointer to field {self.name}.")
        return self._content

    def fill(self, content: AbsContent | dict[str, AbsContent]):
        if self._content is Unfilled:
            raise Exception(f"Cannot fill content before cloning it. 'name': {self.name}.")

        self._content = content
