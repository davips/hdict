from functools import reduce
from operator import rshift
from random import Random

from hdict.abs import AbsAny
from hdict.expression.step.step import AbsStep


class Expr(AbsStep):
    """
    Expressions enable the creation of pipelines of steps (or nested expressions)

    Pipelines should be sampled or fed a hdict to become a resulting hdict.

    >>> from hdict import hdict
    >>> from hdict.expression.expr import Expr
    >>> e = Expr() >> hdict()
    >>> e.show(colored=False)
    ⦑{
        _id: 0000000000000000000000000000000000000000,
        _ids: {}
    }⦒
    >>> e = Expr() >> dict()
    >>> e.show(colored=False)
    ⦑{}⦒
    """

    def __init__(self, *steps):
        self.steps = steps

    def sample(self, rnd: int | Random = None, solve=True):
        from hdict.content.argument import AbsArgument
        from hdict.expression.step.applyout import ApplyOut
        from hdict import cache, hdict
        from hdict.data.frozenhdict import frozenhdict
        from hdict.expression.step.edict import EDict

        lst = []
        for step in self:
            match step:
                case AbsArgument() | ApplyOut():
                    lst.append(step.sample(rnd))
                case cache():
                    lst.append(step)
                case EDict():
                    dct = step.dct.copy()
                    for k, v in dct.items():
                        if isinstance(v, AbsArgument):
                            dct[k] = dct[k].sample(rnd)
                    lst.append(EDict(dct))
                case frozenhdict() | hdict():
                    lst.append(step)
                case AbsAny():  # pragma: no cover
                    raise Exception(f"{type(step)}")
                case x:  # pragma: no cover
                    raise Exception(f"{type(x)}")
        expr = Expr.fromiter(lst)
        return expr.solve() if solve else expr

    def __invert__(self):
        return self.sample()

    @staticmethod
    def fromiter(lst):
        new = Expr()
        new.steps = lst
        return new

    def solve(self):
        from hdict.expression.step.edict import EDict

        gen = (step.dct if isinstance(step, EDict) else step for step in self)
        return reduce(rshift, gen)

    @property
    def unfrozen(self):
        from hdict import frozenhdict

        gen = (step.unfrozen if isinstance(step, frozenhdict) else step for step in self)
        return Expr.fromiter(gen)

    def __iter__(self):
        for step in self.steps:
            if isinstance(step, Expr):
                yield from step
            else:
                yield step

    def show(self, colored=True, key_quotes=False):
        r"""Print textual representation of an expression"""
        print(self.astext(colored, key_quotes))

    def astext(self, colored=True, key_quotes=False):
        r"""
        Textual representation of an expression

        >>> p = Expr({"b":2}, {"a":1})
        >>> p
        ⦑{'b': 2} » {'a': 1}⦒
        >>> p.show()
        ⦑{'b': 2} » {'a': 1}⦒
        """
        from hdict.data.frozenhdict import frozenhdict
        from hdict import hdict

        out = []
        for step in self:
            if isinstance(step, (frozenhdict, hdict)):
                out.append(step.astext(colored=colored, key_quotes=key_quotes))
            else:
                out.append(repr(step))
        return "⦑" + " » ".join(out) + "⦒"

    def __repr__(self):
        return "⦑" + " » ".join(repr(step) for step in self) + "⦒"

    def __str__(self):
        out = []
        for step in self:
            out.append(str(step))
        return "⦑" + " » ".join(out) + "⦒"

    def __bool__(self):  # pragma: no cover
        raise Exception(f"Cannot know the bool value of an expression before evaluating it.")
