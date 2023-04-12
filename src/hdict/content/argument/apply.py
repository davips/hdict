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
from __future__ import annotations

from inspect import isfunction
from inspect import signature
from itertools import chain
from random import Random

from hosh import Hosh

from hdict.content.argument import AbsBaseArgument, AbsArgument
from hdict.content.argument.field import field
from hdict.text.customjson import truncate
from hdict.content.aux_value import f2hosh


class apply(AbsBaseArgument):
    """
    Function application

    Single output application is defined by attribute: 'apply(f).my_output_field'.
    Multioutput application is defined by a call: 'apply(f)("output_field1", "output_field2")'.

    >>> from hdict import apply, value, frozenhdict, _
    >>> f = lambda a, b: a**b
    >>> v = apply(f, 5, b=7)
    >>> v
    λ(5 7)
    >>> g = lambda x, y: x**y
    >>> apply(g, y=value(7777), x=v)
    λ(x=λ(5 7) 7777)

    >>> v2 = apply(f, a=v, b=value(7))
    >>> v2
    λ(a=λ(5 7) 7)
    >>> v.enclosure({}, "j").value
    78125
    >>> v2.enclosure({}, "j")
    λ(a=λ(5 7) 7)
    >>> v2.enclosure({}, "j").value
    17763568394002504646778106689453125

    >>> f = lambda a,b, c=1,d=2,e=13: 0
    >>> apply(f).requirements
    {'a': field(a), 'b': field(b), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> ap = apply(f,3)
    >>> ap.requirements
    {'a': 3, 'b': field(b), 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> ap
    λ(3 b c=default(1) d=default(2) e=default(13))
    >>> ap.enclosure({"b": value(77)}, "j")
    λ(3 b c=1 d=2 e=13)
    >>> ap
    λ(3 b c=default(1) d=default(2) e=default(13))
    >>> d = {"f": ap, "b": 5, "d": 1, "e": field("b")}
    >>> d
    {'f': λ(3 b c=default(1) d=default(2) e=default(13)), 'b': 5, 'd': 1, 'e': field(b)}
    >>> from hdict.data.aux_frozendict import handle_items
    >>> handle_items(d, previous={"b": 5})
    {'b': 5, 'f': λ(3 b c=1 d=2 e=13), 'd': 1, 'e': 5}
    >>> d
    {'f': λ(3 b c=default(1) d=default(2) e=default(13)), 'b': 5, 'd': 1, 'e': field(b)}
    >>> apply(f,3,4).requirements
    {'a': 3, 'b': 4, 'c': default(1), 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': default(2), 'e': default(13)}
    >>> apply(f,3,4,5,6).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': default(13)}
    >>> apply(f,3,4,5,6,7).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7}
    >>> apply(f,d=5).requirements
    {'a': field(a), 'b': field(b), 'c': default(1), 'd': 5, 'e': default(13)}
    >>> f = lambda a,b, *contentarg, c=1,d=2,e=13, **kwargs: 0
    >>> apply(f,3,4,5,6,7,8).requirements
    {'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7, _5: 8}
    >>> apply(f,x=3,e=4,d=5,c=6,b=7,a=8).requirements
    {'a': 8, 'b': 7, 'c': 6, 'd': 5, 'e': 4, 'x': 3}
    >>> apply(f,3,c=77,x=5).requirements
    {'a': 3, 'b': field(b), 'c': 77, 'd': default(2), 'e': default(13), 'x': 5}
    >>> apply(f,b=77,x=5).requirements
    {'a': field(a), 'b': 77, 'c': default(1), 'd': default(2), 'e': default(13), 'x': 5}
    >>> from hdict.content.argument.entry import entry
    >>> a = apply(lambda x: x.value * 7, x=entry("x"))
    >>> c = {"x": 3, "y": entry("x")} >> a.r
    >>> c.show(colored=False)
    {
        x: 3,
        y: ·3,
        r: λ(·x),
        _id: drMRkK24R01dlyw0ye-Rx8Gzac7zxmZUS.toA1gi,
        _ids: {
            x: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            y: KGWjj0iyLAn1RG6RTGtsGE3omZraJM6xO.kvG5pr,
            r: .PtYLSxMYqVXNTh-mnqsQygl4goFXoRrXCtQrTYP
        }
    }
    >>> b = a.x.sample()
    >>> b
    x=λ(·x)
    >>> d = {"x": 3} >> b
    >>> d.x
    21
    >>> a.sampleable
    False
    >>> a.sample()
    λ(·x)
    >>> d["h"] = frozenhdict(a=2)
    >>> d.show(colored=False)
    {
        x: 21,
        h: {
            a: 2,
            _id: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd,
            _ids: {
                a: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29
            }
        },
        _id: Wjqo4.Qw7KBK6NbppnlKT2W3d5KScpptjoCcNsjj,
        _ids: {
            x: .PtYLSxMYqVXNTh-mnqsQygl4goFXoRrXCtQrTYP,
            h: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd
        }
    }
    >>> a = apply(lambda x: x.value * 7).x
    >>> d >>= a
    >>> d.show(colored=False)
    {
        x: λ(x=21),
        h: {
            a: 2,
            _id: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd,
            _ids: {
                a: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29
            }
        },
        _id: 5fUCSwb7D633jeGv.xMb006XT8Ulr18os.KxyeTH,
        _ids: {
            x: -89UidPh6BgYdYYTx4nxewuDpdilgWzm4O6adFwc,
            h: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd
        }
    }
    >>> a = apply(lambda x: x.value * 7, entry("x")).x
    >>> d >>= a
    >>> d.show(colored=False)
    {
        x: λ(λ(x=21)),
        h: {
            a: 2,
            _id: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd,
            _ids: {
                a: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29
            }
        },
        _id: pEhqOs9sPjot-eiGgJbKQ5j7aTL1MySiBaoTj0r4,
        _ids: {
            x: mmdYysfo0-rbXPLWBaqHKdxGkR9xwyihdlfv-q4B,
            h: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd
        }
    }
    >>> d >>= {"b" : 2, "c": entry("b")}
    >>> d.show(colored=False)
    {
        x: λ(λ(x=21)),
        h: {
            a: 2,
            _id: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd,
            _ids: {
                a: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29
            }
        },
        b: 2,
        c: ·2,
        _id: WoI36oD8iHnd81y0q-VTpbFoN2rhdAbRGOk1yBK5,
        _ids: {
            x: mmdYysfo0-rbXPLWBaqHKdxGkR9xwyihdlfv-q4B,
            h: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd,
            b: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29,
            c: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29
        }
    }
    >>> d >>= {"b" : (2, 3), ("a1", "b1"): [0, 1]}
    >>> d >>= {("a2", "b2"): _.b}
    >>> d >>= {("a3", "b3"): entry("b")}
    >>> d.show(colored=False)  # TODO: improve output for subvalues (and backtracking in general for pointer-like entries)
    {
        x: λ(λ(x=21)),
        h: {
            a: 2,
            _id: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd,
            _ids: {
                a: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29
            }
        },
        b: [
            2,
            3
        ],
        c: ·2,
        a1: 0,
        b1: 1,
        a2: "(2, 3)→0",
        b2: "(2, 3)→1",
        a3: ·(2, 3)→0,
        b3: ·(2, 3)→1,
        _id: jY2TGGf9ZSvPk7k3Mu4bgeJJXZ45Gwwye.wPVBgX,
        _ids: {
            x: mmdYysfo0-rbXPLWBaqHKdxGkR9xwyihdlfv-q4B,
            h: GfMhwM5bo6OzIpngAf8Ruro6.QgOv2kb0nbj0mgd,
            b: -a.WUGANQp6aVgbRCtUljlgs12HNtJ-dJOAgSZWk,
            c: k3PWYRxIEc0lEvD1f6rbnk.36RAD5AyfROy1aT29,
            a1: M7HyZUgSF.ZSmBEMFcDkiZBQz00wU9pGF3DoRiDu,
            b1: DYu5bfVvb6FOhBCWNsss4wsEWHZYTbKnsVgoWFvl,
            a2: GfnITQ6RdDtm4F-F0UuU8fOJX1DZIBZG5RWBM8wm,
            b2: QznFPbiCaMRZKUoFhdLxMKYQf3ujIe1zDl9G5Rq-,
            a3: GfnITQ6RdDtm4F-F0UuU8fOJX1DZIBZG5RWBM8wm,
            b3: QznFPbiCaMRZKUoFhdLxMKYQf3ujIe1zDl9G5Rq-
        }
    }
    """

    _sampleable, isfield, _requirements = None, False, None

    def __init__(self, appliable: callable | apply | field, *applied_args, fhosh: Hosh = None, _sampleable=None, **applied_kwargs):
        from hdict.content.argument.aux_apply import handle_args

        self.appliable = appliable
        if isinstance(fhosh, str):  # pragma: no cover
            fhosh = Hosh.fromid(fhosh)

        if isinstance(appliable, apply):  # "clone" mode
            self.fhosh = fhosh or appliable.fhosh
            self.fargs, self.fkwargs = appliable.fargs.copy(), appliable.fkwargs.copy()
            self.isfield = appliable.isfield
            self._sampleable = appliable.sampleable if _sampleable is None else _sampleable
            self.appliable = appliable.appliable
        elif isinstance(appliable, field):
            # TODO: o que era isso mesmo?::  "function will be provided by hdict"-mode constrains 'applied_args'
            self.fhosh = fhosh
            self.fargs, self.fkwargs = handle_args(None, applied_args, applied_kwargs)
            self.isfield = True
            self._sampleable = _sampleable
        elif callable(appliable):
            if not isfunction(appliable):  # "not function" means "custom callable"
                if not hasattr(appliable, "__call__"):  # pragma: no cover
                    raise Exception(f"Cannot infer method to apply non custom callable type '{type(appliable).__name__}'.")
                if not hasattr(appliable, "hosh"):  # pragma: no cover
                    raise Exception(f"Missing 'hosh' attribute while applying custom callable class '{type(appliable).__name__}'")
                # noinspection PyUnresolvedReferences
                sig = signature(appliable.__call__)
                # noinspection PyUnresolvedReferences
                self.fhosh = fhosh or appliable.hosh
            else:
                self.fhosh = f2hosh(appliable) if fhosh is None else fhosh
                sig = signature(appliable)

            # Separate positional parameters from named parameters looking at 'f' signature.
            self.fargs, self.fkwargs = handle_args(sig, applied_args, applied_kwargs)
            self._sampleable = _sampleable
        else:  # pragma: no cover
            raise Exception(f"Cannot apply type '{type(appliable).__name__}'.")

    @property
    def sampleable(self):
        if self._sampleable is None:
            gen = (req.sampleable for req in self.fargs.values())
            kwgen = (req.sampleable for req in self.fkwargs.values())
            self._sampleable = any(gen) or any(kwgen)
        return self._sampleable

    @property
    def ahosh(self):
        return self.fhosh.rev  # 'f' identified as an appliable function

    def clone(self, _sampleable=None):
        return apply(self, _sampleable=_sampleable)

    def sample(self, rnd: int | Random = None):
        if not self.sampleable:
            return self
        clone = self.clone(_sampleable=False)
        for k, v in clone.fargs.items():
            clone.fargs[k] = v.sample(rnd)
        for k, v in clone.fkwargs.items():
            clone.fkwargs[k] = v.sample(rnd)
        return clone

    def enclosure(self, data, key):
        from hdict.content.entry.closure import Closure

        return Closure(self, data, [key])

    def __call__(self, *out, **kwout):
        from hdict.expression.step.applyout import ApplyOut

        if not (out or kwout):  # pragma: no cover
            raise Exception(f"At least one output field must be specified to apply.")

        if out and kwout:  # pragma: no cover
            raise Exception(f"Cannot mix translated (**kwargs) and non translated (*args) outputs.")
        if len(out) == 1:
            out = out[0]
        return ApplyOut(self, out or tuple(kwout.items()))

    def __getattr__(self, item):
        # REMINDER: Work around getattribute missing all properties.
        if item not in ["ahosh", "requirements", "hosh"]:
            from hdict.expression.step.applyout import ApplyOut

            return ApplyOut(self, item)
        return self.__getattribute__(item)  # pragma: no cover

    def __rshift__(self, other):  # pragma: no cover
        raise Exception(f"Cannot pipeline an application before specifying the output field.")

    def __rrshift__(self, other):  # pragma: no cover
        raise Exception(f"Cannot apply before specifying the output field.")

    def __mul__(self, other):  # pragma: no cover
        raise Exception(f"Cannot pipeline an application before specifying the output field.")

    def __rmul__(self, other):  # pragma: no cover
        raise Exception(f"Cannot apply before specifying the output field.")

    def __repr__(self):
        from hdict.content.value import value
        from hdict.content.argument.entry import entry

        lst = []
        for param, content in sorted(chain(self.fargs.items(), self.fkwargs.items())):
            match content:
                case field(name=param):
                    lst.append(f"{param}")
                case entry(name=param):
                    lst.append(repr(content))
                case value():
                    lst.append(truncate(repr(content), width=7))
                case AbsArgument():
                    lst.append(f"{param}={repr(content)}")
                case _:  # pragma: no cover
                    raise Exception(f"Canoot repr `{type(content)}")
        return f"λ({' '.join(lst)})"

    @property
    def requirements(self):
        if self._requirements is None:
            self._requirements = {k: v for k, v in sorted(chain(self.fargs.items(), self.fkwargs.items()))}
        return self._requirements
