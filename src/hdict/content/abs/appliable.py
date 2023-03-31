from hosh import Hosh

from hdict import field, apply
from hdict.content.abs.any import AbsAny


class AbsAppliable(AbsAny):
    """Lazy content that will be nested by a Closure object inside a hdict field"""
    appliable: callable | apply | field
    fargs: dict
    fkwargs: dict
    ahosh: Hosh
    isfield: bool
