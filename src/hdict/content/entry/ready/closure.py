from __future__ import annotations

from itertools import chain

from hosh import ø

from hdict import field
from hdict.content.argument import AbsArgument
from hdict.content.argument.apply import apply
from hdict.content.argument.default import default
from hdict.content.entry import AbsEntry, Unevaluated
from hdict.content.entry.aux_closure import handle_arg
from hdict.content.entry.ready import AbsReadyEntry
from hdict.content.entry.unready import AbsUnreadyEntry
from hdict.customjson import truncate


class Closure(AbsReadyEntry):
    unready = False

    def __init__(self, application: apply, result: dict[str, AbsEntry], ignore):
        from hdict.aux_frozendict import handle_item
        self.application = application
        hosh = ø

        # REMINDER: kwargs are alphabetically sorted to ensure we keep the same resulting hosh
        #   no matter in which order the keyworded parameters are passed to the function.
        #           If the order in which positional args are defined in the function changes, fhosh will reflect the change.
        arg = None
        fargs, fkwargs, discarded_defaults = {}, {}, set()
        for key, val in application.fargs.items():
            arg = handle_arg(key, val, result, discarded_defaults, ignore)
            if arg is None:
                self.unready = True
            else:
                fargs[key] = arg
                hosh *= arg.hosh
        for key, val in sorted(application.fkwargs.items()):
            arg = handle_arg(key, val, result, discarded_defaults, ignore)
            if arg is None:
                self.unready = True
            else:
                fkwargs[key] = arg
                hosh *= arg.hosh

        if application.isfield:
            appliable_entry = handle_item(application.appliable, result, ignore)
            if isinstance(appliable_entry, AbsUnreadyEntry):
                self.unready = True
            else:
                hosh *= appliable_entry.hosh.rev

            def f():
                args = (x.value for x in fargs.values())
                kwargs = {k: v.value for k, v in fkwargs.items()}
                return appliable_entry.value(*args, **kwargs)
        else:
            hosh *= application.ahosh
            appliable_function = application.appliable

            def f():
                args = (x.value for x in fargs.values())
                kwargs = {k: v.value for k, v in fkwargs.items()}
                return appliable_function(*args, **kwargs)
        self.f = f
        self.hosh = hosh
        self.fargs = fargs
        self.fkwargs = fkwargs
        self.discarded_defaults = discarded_defaults

    @property
    def value(self):
        if self._value == Unevaluated:
            self._value = self.f()
            # del self.application  # TODO: delete clasure.application inside each subvalue?
        return self._value

    def __repr__(self):
        from hdict import value

        lst = []
        for param, content in chain(self.application.fargs.items(), sorted(self.application.fkwargs.items())):
            pre = "" if isinstance(param, int) else f"{param}="
            match content:
                case value():
                    lst.append(truncate(repr(content), width=7))
                case default() if param in self.discarded_defaults:
                    lst.append(f"{param}")
                case default(value=v):
                    lst.append(f"{param}={v}")
                case field(name) if name == param:
                    lst.append(f"{param}")
                case field(name):
                    lst.append(f"{pre}{name}")
                case AbsArgument():
                    lst.append(f"{pre}{repr(content)}")
                case _:
                    raise Exception(type(content))
        return f"λ({' '.join(lst)})"
