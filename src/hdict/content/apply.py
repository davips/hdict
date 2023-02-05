#  Copyright (c) 2023. Davi Pereira dos Santos
#  This file is part of the hdict project.
#  Please respect the license - more about this in the section (*) below.
#
#  hdict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  hdict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with hdict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#

from functools import reduce
from inspect import isfunction
from inspect import signature
from itertools import chain
from operator import mul
from random import Random
from typing import Union

from hdict.content.abs.abscloneable import AbsCloneable
from hdict.content.abs.abssampleable import AbsSampleable
from hdict.content.field import field
from hdict.content.handling import Unevaluated, handle_args
from hdict.content.value import value
from hdict.customjson import truncate
from hdict.hoshfication import f2hosh
from hosh import Hosh
from hosh.misc import hoshes


class apply(AbsCloneable, AbsSampleable):
    """
    >>> from hdict import apply
    >>> f = lambda a, b: a**b
    >>> v = apply(f, 5, b=7)
    >>> v
    λ(5 7)
    >>> g = lambda x, y: x**y
    >>> v.isevaluated
    False
    >>> apply(g, y=value(7777), x=v)
    λ(x=λ(5 7) 7777)

    >>> v2 = apply(f, a=v, b=value(7))
    >>> v2
    λ(a=λ(5 7) 7)
    >>> v.finish({})
    >>> v.value, v2
    (78125, λ(a=78125 7))
    >>> v2.finish({})
    >>> v2.value, v2
    (17763568394002504646778106689453125, 17763568394002504646778106689453125)

    >>> f = lambda a,b, c=1,d=2,e=13: 0
    >>> apply(f).requirements
    {'a': field('a'), 'b': field('b'), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> ap = apply(f,3)
    >>> ap.requirements
    {'a': 3, 'b': field('b'), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> ap
    λ(3 b c=default(1) d=default(2) e=default(13))
    >>> ap.finish({"b": value(77)})
    >>> ap
    λ(3 b c=default(1) d=default(2) e=default(13))
    >>> from hdict.content.handling import handle_values
    >>> d = {"f": ap, "b": 5, "d": 1, "e": field("b")}
    >>> d
    {'f': λ(3 b c=default(1) d=default(2) e=default(13)), 'b': 5, 'd': 1, 'e': field('b')}
    >>> handle_values(d)
    >>> d
    {'f': λ(3 b 1 d b), 'b': 5, 'd': 1, 'e': b}
    >>> apply(f,3,4).requirements
    {'a': 3, 'b': 4, 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5,6).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': default(13)}
    >>> apply(f,3,4,5,6,7).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7}
    >>> apply(f,d=5).requirements
    {'a': field('a'), 'b': field('b'), 'c': default(1), 'd': 5, 'e': default(13)}
    >>> f = lambda a,b, *contentarg, c=1,d=2,e=13, **kwargs: 0
    >>> apply(f,3,4,5,6,7,8).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7, _5: 8}
    >>> apply(f,x=3,e=4,d=5,c=6,b=7,a=8).requirements
    {'a': 8, 'b': 7, 'c': 6, 'd': 5, 'e': 4, 'x': 3}
    >>> apply(f,3,c=77,x=5).requirements
    {'a': 3, 'b': field('b'), 'c': 77, 'd': default(2), 'e': default(13), 'x': 5}
    >>> apply(f,b=77,x=5).requirements
    {'a': field('a'), 'b': 77, 'c': default(1), 'd': default(2), 'e': default(13), 'x': 5}
    """

    out = None
    _value = Unevaluated
    _hosh = None

    def __init__(self, f: Union[callable, "apply", field], *applied_args, fhosh: Hosh = None, **applied_kwargs):
        self.f = f
        if isinstance(fhosh, str):  # pragma: no cover
            fhosh = Hosh.fromid(fhosh)
        if isinstance(f, apply):  # "clone" mode
            fun = f.fun
            self.f = f.f
            self.fhosh = f.fhosh
            self.args = {k: req.clone() if isinstance(req, AbsCloneable) else req for k, req in f.args.items()}
            self.kwargs = {k: req.clone() if isinstance(req, AbsCloneable) else req for k, req in f.kwargs.items()}
            from hdict.content.default import default
        elif isinstance(f, field):  # "function will be provided by hdict"-mode constrains 'applied_args'
            self.fhosh = fhosh
            fun = lambda *args, **kwargs: f.value(*args, **kwargs)
            self.args, self.kwargs = handle_args(None, applied_args, applied_kwargs)
        elif callable(fun := f):
            if not isfunction(fun):  # "not function" means "custom callable"
                if not hasattr(fun, "__call__"):  # pragma: no cover
                    raise Exception(f"Cannot infer method to apply non custom callable type '{type(fun)}'.")
                if not hasattr(fun, "hosh"):  # pragma: no cover
                    raise Exception(f"Missing 'hosh' attribute while applying custom callable class '{type(fun)}'")
                # noinspection PyUnresolvedReferences
                sig = signature(fun.__call__)
                self.fhosh = fhosh
            else:
                self.fhosh = f2hosh(fun) if fhosh is None else fhosh
                sig = signature(fun)

            # Separate positional parameters from named parameters looking at 'f' signature.
            self.args, self.kwargs = handle_args(sig, applied_args, applied_kwargs)
        else:  # pragma: no cover
            raise Exception(f"Cannot apply type '{type(f)}'.")
        self._fun = fun
        self.requirements = {k: v for k, v in sorted((self.args | self.kwargs).items())}
        # Requirements (dependencies stub) are alphabetically sorted to ensure we keep the same resulting hosh no matter in which order the parameters are defined in the function.

    @property
    def ahosh(self):
        return self.fhosh.rev  # 'f' identified as an appliable function

    def finish(self, data):
        if self.finished:  # pragma: no cover
            raise Exception(f"Cannot finish an application twice.")
        if isinstance(self.f, apply):  # pragma: no cover
            raise Exception(f"Why applying another apply object?")
        if isinstance(self.f, AbsCloneable) and not self.f.finished:
            self.f.finish(data)
        if self.fhosh is None:
            self.fhosh = self.f.hosh
        reqs = self.requirements
        for kreq, req in reqs.items():
            if isinstance(req, AbsCloneable) and not req.finished:
                req.finish(data)
        self._finished = True

    def clone(self):
        return apply(self)

    @property
    def hosh(self):
        if not self.finished:  # pragma: no cover
            from hdict import sample

            if any(isinstance(x, sample) for x in self.requirements.values()):
                raise Exception(f"Cannot know the identity of this hdict or apply object before sampling. Provided callable:", self.f)
            raise Exception(f"Cannot know apply.hosh before finishing object apply. Provided callable:", self.f)
        if self._hosh is None:
            self._hosh = reduce(mul, chain(hoshes(self.requirements.values()), [self.ahosh]))
        return self._hosh

    @property
    def value(self):
        if self._value == Unevaluated:
            if not self.finished:  # pragma: no cover
                raise Exception(f"Cannot access apply.value before finishing object '{self.fhosh}'.")
            args = (x.value for x in self.args.values())
            kwargs = {k: v.value for k, v in self.kwargs.items()}
            self._value = self._fun(*args, **kwargs)
        return self._value

    @property
    def fun(self):
        return self._fun

    @property
    def isevaluated(self):
        return self._value != Unevaluated

    def sample(self, rnd: int | Random = None):
        clone = self.clone()
        args = clone.args
        kwargs = clone.kwargs
        reqs = clone.requirements
        for k, v in args.items():
            if isinstance(v, AbsSampleable):
                args[k] = reqs[k] = v.sample(rnd)
        for k, v in kwargs.items():
            if isinstance(v, AbsSampleable):
                kwargs[k] = reqs[k] = v.sample(rnd)
        return clone

    def __call__(self, *out, **kwout):
        from hdict.content.applyout import applyOut

        if out and kwout:  # pragma: no cover
            raise Exception(f"Cannot mix translated and non translated outputs.")
        return applyOut(self, out or tuple(kwout.items()))

    def __getattr__(self, item):
        # REMINDER: Work around getattribute missing all properties.
        if item not in ["isevaluated", "fun", "value", "hosh", "ahosh"]:
            from hdict.content.applyout import applyOut

            return applyOut(self, item)
        return self.__getattribute__(item)  # pragma: no cover

    def __repr__(self):
        if not self.isevaluated:
            from hdict.content.default import default

            lst = []
            for param, content in self.requirements.items():
                if isinstance(content, field):
                    txt = content.name
                elif isinstance(content, (apply, default)):
                    txt = f"{param}={repr(content)}"
                else:
                    txt = truncate(repr(content), width=7)
                lst.append(txt)
            return f"λ({' '.join(lst)})"
        return repr(self._value)
