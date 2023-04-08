from functools import reduce
from itertools import chain
from operator import rshift
from random import Random

from hdict.abs import AbsAny


class Expr(AbsAny):
    """
    Expressions enable the creation of pipelines of steps

    Pipelines should be sampled or fed a hdict to become a resulting hdict.
    """

    def __init__(self, *steps):
        self.steps = steps

    def sample(self, rnd: int | Random = None, solve=True):
        from hdict.content.argument import AbsArgument
        from hdict.applyout import ApplyOut

        lst = []
        for step in self:
            match step:
                case AbsArgument() | ApplyOut():
                    lst.append(step.sample(rnd))
                case AbsAny():
                    raise Exception(f"{type(step)}")
                case dict():
                    dct = step.copy()
                    for k, v in dct.items():
                        if isinstance(v, AbsArgument):
                            dct[k] = dct[k].sample(rnd)
                    lst.append(dct)
                case _:
                    raise Exception(f"")
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
        return reduce(rshift, self)

    def roperate(self, left, solve):
        from hdict import hdict, frozenhdict

        match left:
            case hdict() | frozenhdict():
                expr = Expr(left, self)
            case dict():
                expr = Expr(hdict(left), self)
            case _:
                return NotImplemented  # pragma: no cover
        return expr.solve() if solve else expr

    def __rrshift__(self, left):
        return self.roperate(left, True)

    def __rmul__(self, left):
        return self.roperate(left, False)

    def __iter__(self):
        for step in self.steps:
            if isinstance(step, Expr):
                yield from step
            else:
                yield step

    def __repr__(self):
        return " » ".join(repr(step) for step in self)

    def __str__(self):
        out = []
        for step in self:
            out.append(str(step))
        return " » ".join(out)

    def show(self, colored=True, key_quotes=False):
        r"""Print textual representation of an expression"""
        print(self.astext(colored, key_quotes))

    def astext(self, colored=True, key_quotes=False):
        r"""
        Textual representation of an expression

        >>> p = Expr({"b":2}, {"a":1})
        >>> p
        {'b': 2} » {'a': 1}
        >>> p.show()
        {'b': 2} » {'a': 1}
        """
        from hdict.frozenhdict import frozenhdict
        from hdict import hdict

        out = []
        for step in self:
            if isinstance(step, (frozenhdict, hdict)):
                out.append(step.astext(colored=colored, key_quotes=key_quotes))
            else:
                out.append(repr(step))
        return " » ".join(out)
