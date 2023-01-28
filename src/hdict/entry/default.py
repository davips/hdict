from hdict.entry.abscontent import AbsContent
from hdict.hoshfication import v2hosh
from hosh import Hosh


class default(AbsContent):
    def __init__(self, name: str, value: object, hosh: Hosh = None, hdict=None):
        from hdict.entry.field import field
        if isinstance(value, AbsContent) and not isinstance(value, field):
            raise Exception(f"Can only nest 'field' or ordinary values inside a 'default' object: '{type(value)}")
        self.name, self.value = name, value
        self._hosh = Hosh.fromid(hosh) if isinstance(hosh, str) else hosh
        self.hdict = hdict
        self.isevaluated = True

    @property
    def hosh(self):
        if self._hosh is None:
            self._hosh = v2hosh(self.value)
        return self._hosh

    def clone(self):
        from hdict.entry.field import field
        value = self.value.clone if isinstance(self.value, field) else self.value
        return default(self.name, value, self._hosh)

    def __repr__(self):
        return f"default({repr(self.value)})"
