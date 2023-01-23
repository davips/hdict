from hdict.entry.absnestedarg import AbsNestedArg
from hosh import Hosh


class field(AbsNestedArg):
    def __init__(self, name: str, hosh: Hosh = None, ispositional: bool = None):
        self.name, self.hosh, self.ispositional = name, hosh, ispositional

    def clone(self, hosh: Hosh = None):
        return field(self.name, hosh=hosh or self.hosh)
