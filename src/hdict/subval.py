from hosh import Hosh

from hdict.absval import AbsVal


class SubVal(AbsVal):
    def __init__(self, parent: AbsVal, item: [int, str], hosh: Hosh):
        self.parent, self.item, self.hosh = parent, item, hosh
        self.isevaluated = self.parent.isevaluated
        self.__repr__ = self.parent.__repr__

    @property
    def value(self):
        # noinspection PyUnresolvedReferences
        return self.parent.value[self.item]
