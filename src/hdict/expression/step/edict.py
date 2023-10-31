from dataclasses import dataclass

from hdict.expression.step.step import AbsStep
from hdict.text.customjson import stringfy


@dataclass
class EDict(AbsStep):
    """
    Wrapper for dict inside an Expr object

    Useful to keep the step as a `dict` as long as possible, specially when printing the expression.
    """

    dct: dict

    def __repr__(self):
        return stringfy(self.dct)

    def __bool__(self):
        return bool(self.dct)
