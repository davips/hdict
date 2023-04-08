from __future__ import annotations

from itertools import chain

from hosh import ø

from hdict.content.argument import AbsArgument
from hdict.content.argument.apply import apply
from hdict.content.argument.default import default
from hdict.content.entry import AbsEntry, Unevaluated
from hdict.content.entry.aux_closure import handle_arg
from hdict.customjson import truncate


class Closure(AbsEntry):
    def __init__(self, application: apply, data: dict[str, AbsEntry], out: list):
        from hdict.aux_frozendict import handle_item

        self.application = application
        self.out = out
        self.torepr = {}
        hosh = ø
        arg = None
        fargs, fkwargs, discarded_defaults = {}, {}, set()
        sorted_fargs = zip(map(str, application.fargs), application.fargs.items())
        for idx, tup in sorted(chain(sorted_fargs, application.fkwargs.items())):  # We sort by keys for a deterministic hosh.
            if isinstance(tup, tuple):
                key, val = tup
                arg = handle_arg(key, val, data, discarded_defaults, out, self.torepr)
                fargs[key] = arg
            else:
                key, val = idx, tup
                arg = handle_arg(key, val, data, discarded_defaults, out, self.torepr)
                fkwargs[key] = arg
            hosh *= arg.hosh

        if application.isfield:
            appliable_entry = handle_item(application.appliable.name, application.appliable, data)
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
        self.discarded_defaults = discarded_defaults

    @property
    def value(self):
        if self._value == Unevaluated:
            self._value = self.f()
            # del self.application  # TODO: delete clasure.application inside each subvalue?
        return self._value

    def __repr__(self):
        from hdict import value
        from hdict import field

        lst = []
        for param, content in self.torepr.items():
            pre = "" if isinstance(param, int) else f"{param}="
            match content:
                case value():
                    lst.append(truncate(repr(content), width=7))
                case default() if param in self.discarded_defaults:
                    lst.append(f"{param}")
                case default(value=v):
                    lst.append(f"{param}={v}")
                case field(name) if name in self.out:
                    lst.append(f"{repr(content)}")
                case field(name) if name == param:
                    lst.append(f"{param}")
                case field(name):
                    lst.append(f"{pre}{name}")
                case AbsArgument():
                    lst.append(f"{pre}{repr(content)}")
                case _:
                    raise Exception(type(content))
        return f"λ({' '.join(lst)})"
