from hdict.entry.abscontent import AbsContent
from hdict.hoshfication import v2hosh
from hosh import Hosh


class default(AbsContent):
    def __init__(self, name: str, value: object, hosh: Hosh = None, hdict=None):
        if isinstance(value, AbsContent):
            raise Exception(f"Cannot nest AbsContent object inside a 'default' object: '{type(value)}")
        self.name, self.value = name, value
        if isinstance(hosh, str):
            hosh = Hosh.fromid(hosh)
        self.hosh = v2hosh(value) if hosh is None else hosh
        self.hdict = hdict
        self.isevaluated = True

    def __repr__(self):
        return f"default({self.value})"
