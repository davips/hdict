from __future__ import annotations

from dataclasses import dataclass

from hdict.content.abs.appliable import AbsAppliable
from hdict.content.abs.entry import AbsEntry
from hosh import ø

from hdict import apply, value
from hdict.content.subcontent import subcontent


@dataclass
class Unevaluated:
    n = 0


Unevaluated = Unevaluated()


class Closure(AbsEntry):
    _value = Unevaluated

    def __init__(self, content: AbsAppliable, result: dict[str, AbsEntry]):
        from hdict.aux import handle_applied_arg
        from hdict.content import MissingFieldException
        from hdict.aux import traverse_field

        self.content = content

        # TODO:  Remove redundance: só precisa calcular isso tudo uma vez pra todos os subcontents.
        hosh = ø
        fargs, fkwargs = [], {}
        for key, val in content.fargs.items():
            app = handle_applied_arg(key, val, result)
            fargs.append(app)
            hosh *= app.hosh
        for key, val in content.fkwargs.items():
            app = handle_applied_arg(key, val, result)
            fkwargs[key] = app
            hosh *= app.hosh
        hosh *= content.ahosh

        if content.isfield:
            name = content.appliable.name
            if name not in result:
                raise MissingFieldException(name)
            appliable_value = traverse_field(name, result)

            def f():
                args = (x.value for x in fargs)
                kwargs = {k: v.value for k, v in fkwargs.items()}
                return appliable_value.value(*args, *kwargs)
        else:
            appliable_function = content.appliable

            def f():
                args = (x.value for x in fargs)
                kwargs = {k: v.value for k, v in fkwargs.items()}
                return appliable_function(*args, *kwargs)
        self.f = f
        if isinstance(content, apply):
            self.hosh = hosh
        elif isinstance(content, subcontent):
            self.hosh = hosh[content.index: content.n]

    @property
    def value(self):
        if self._value == Unevaluated:
            self._value = self.f()
            # del self.content  # TODO: will this break twin subcontents?
        return self._value

    @property
    def isevaluated(self):
        """
        >>> from hdict import apply
        >>> closure(apply(lambda x, y: x + y).x).isevaluated
        False
        """
        return self._value != Unevaluated

    def __repr__(self):
        if self.isevaluated:
            return repr(self.value)
        return repr(self.content)
