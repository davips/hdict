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
from types import NoneType
from typing import Union

from hosh import Hosh

from hdict.content.apply import apply
from hdict.content.default import default
from hdict.content.field import field
from hdict.content.sample import sample
from hdict.content.value import value
from hdict.frozenhdict import frozenhdict
from hdict.hdict_ import hdict


class _(frozenhdict):
    Ø = frozenhdict()

    def __call__(self, f_or_dictionary: Union[callable, "apply", field] = None, *applied_args, fhosh: Hosh = None, **kwargs):
        if isinstance(f_or_dictionary, (NoneType, dict)):
            if fhosh is not None:  # pragma: no cover
                raise Exception(f"Cannot use '_()' as hdict constructor and provide 'fhosh' at the same time.")
            if f_or_dictionary is None:
                f_or_dictionary = kwargs
                kwargs = {}
            return hdict(f_or_dictionary, **kwargs)
        return apply(f_or_dictionary, *applied_args, fhosh=fhosh, **kwargs)

    def __getattr__(self, item):
        return field(item)

    def __getitem__(self, item):
        return sample(*item)


_ = _()
Ø = _.Ø
