from hdict.abs import AbsAny


class AbsStep(AbsAny):
    """
    An operand (single step object) or an expression (multiple steps object)

    >>> from hdict import cache, apply
    >>> e = dict() * apply(lambda: None).a * (cache({}) >> dict())
    >>> e.show(colored=False)
    ⦑{} » a=λ() » ↑↓`dict` » {}⦒

    Operands:
        dict
        hEf:        hdict, Empty, frozenhdict
        AbsStep:    ApplyOut, cache, Expr

    Rules for operations:
        dict >> hEf         =   frozenhdict.py  solve
        dict >> AbsStep     =   step.py         solve

        hEf >> dict         =   frozenhdict.py solve
        hEf >> hEf          =   frozenhdict.py solve
        hEf >> AbsStep      =   frozenhdict.py solve

        AbsStep >> dict     =   step.py
        AbsStep >> hEf      =   step.py
        AbsStep >> AbsStep  =   step.py


        dict * hEf          =   frozenhdict.py
        dict * AbsStep      =   step.py
        hEf * ?             =   frozenhdict.py
        AbsStep * ?         =   step.py
    """

    def __rshift__(self, other):
        return self * other

    def __mul__(self, other):
        from hdict import hdict, frozenhdict
        from hdict.expression.step.edict import EDict
        from hdict.expression.expr import Expr

        match other:
            case AbsStep() | hdict() | frozenhdict():
                return Expr(self, other)
            case dict():
                return Expr(self, EDict(other))
            case _:  # pragma: no cover
                return NotImplemented

    def __rrshift__(self, left):
        from hdict import hdict
        from hdict import frozenhdict

        if isinstance(left, dict) and not isinstance(left, (hdict, frozenhdict)):
            return hdict(left) >> self
        return NotImplemented  # pragma: no cover

    def __rmul__(self, left):
        from hdict import frozenhdict
        from hdict.expression.step.edict import EDict
        from hdict.expression.expr import Expr
        from hdict import hdict

        if isinstance(left, dict) and not isinstance(left, (hdict, frozenhdict)):
            return Expr(EDict(left), self)
        return NotImplemented  # pragma: no cover
