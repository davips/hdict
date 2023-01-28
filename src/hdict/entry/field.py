from hdict.entry.abscontent import AbsContent
from hosh import Hosh


class field(AbsContent):
    """
    Pointer to a field
    """

    content = None

    def __init__(self, name: str, hosh: Hosh = None):
        self.name, self._hosh = name, hosh

    @property
    def finished(self):
        return self.content is not None

    def finish(self, data):
        from hdict.entry.apply import apply
        if self.content is not None:
            raise Exception(f"Cannot finish a field pointer twice. name: {self.name}; hosh: {self.hosh}")
        if self.name not in data:
            raise Exception(f"Missing field '{self.name}'")
        self.content = data[self.name]
        if isinstance(self.content, (apply, field)) and not self.content.finished:
            self.content.finish(data)

    @property
    def hosh(self):
        if self.content is None:
            raise Exception(f"Cannot know hosh before finishing pointer to field '{self.name}'.")
        if self._hosh is None:
            self._hosh = self.content.hosh
        return self._hosh

    @property
    def value(self):
        if self.content is None:
            raise Exception(f"Cannot access value before finishing pointer to field '{self.name}'.")
        return self.content.value

    @property
    def isevaluated(self):
        return self.content and self.content.isevaluated

    def clone(self):
        return field(self.name, self._hosh)

    def __repr__(self):
        if self.content is None:
            txt = f"field('{self.name}'"
            txt += ")" if self._hosh is None else ", '{self._hosh}')"
            return txt
        return repr(self.content) if isinstance(self.content, field) else self.name
