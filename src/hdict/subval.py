from hosh import Hosh

from hdict.entry.absarg import AbsArg


class SubVal(AbsArg):
    def __init__(self, parent: AbsArg, item: [int, str], hosh: Hosh):
        self.parent, self.item, self.hosh = parent, item, hosh
        self.isevaluated = self.parent.isevaluated
        self.__repr__ = self.parent.__repr__

    @property
    def value(self):
        # noinspection PyUnresolvedReferences
        return self.parent.value[self.item]
