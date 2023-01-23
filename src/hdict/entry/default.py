from dataclasses import dataclass

from hdict.entry.absnestedarg import AbsNestedArg
from hosh import Hosh


@dataclass
class default(AbsNestedArg):
    hosh: Hosh = None
    ispositional: bool = None

    def clone(self, hosh: Hosh = None):
        return default(hosh=hosh or self.hosh)
