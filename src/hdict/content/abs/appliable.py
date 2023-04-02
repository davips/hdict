from __future__ import annotations
from typing import Union

from hosh import Hosh

from hdict.content.field import field


class asAppliable:
    isfield: bool
    fargs: dict
    fkwargs: dict
    ahosh: Hosh
    appliable: Union[callable, field]
