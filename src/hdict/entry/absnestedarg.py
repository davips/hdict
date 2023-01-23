from functools import cached_property

from hdict.entry.absarg import AbsArg
from hosh import Hosh


class AbsNestedArg(AbsArg):
    hosh: Hosh = None
    _nested: AbsArg = None

    @cached_property
    def nested(self):  # pragma: no cover
        if self._nested is None:
            raise Exception(f"Cannot access value of unfinished value holder 'field {self.name}'")
        return self._nested

    @cached_property
    def value(self):  # pragma: no cover
        return self.nested.value

    @cached_property
    def isevaluated(self):  # pragma: no cover
        return self.nested.isevaluated

    def nest(self, nested: AbsArg):
        self._nested = nested
