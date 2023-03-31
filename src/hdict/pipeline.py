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
from itertools import chain
from operator import rshift
from random import Random

from hdict.content.abs.sampling import withSampling
from hdict.content.abs.pipeable import AbsPipeable


class pipeline(AbsPipeable, withSampling):
    """
    Sequence of steps, tries to solve on update, resulting in a hdict/frozenhdict

    >>> from hdict import apply
    >>> p = dict(x=5) >> apply(lambda x, y: x + y).r
    >>> p.show(colored=False)
    {
        x: 5,
        _id: PRj.5PqNWuPfNvmXl83el.sSMPcTS02ZIl4.K.5k,
        _ids: {
            x: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2
        },
        y: ✗ first missing field ✗
    } » r=λ(x y)
    >>> p2 = dict(y=7) >> p
    >>> p2.show(colored=False)
    {
        y: 7,
        x: 5,
        r: λ(x y),
        _id: e6de0.-QdmYbais2opJzX8momKCV2jdGGSu6kV5H,
        _ids: {
            y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            r: orsvTbm.vJYQS4Jw0Z-oGjcGdFFyDWp9CVj7M1CN
        }
    }
    >>> ({} >> p2).show(colored=False)
    {} » {
        y: 7,
        x: 5,
        r: λ(x y),
        _id: e6de0.-QdmYbais2opJzX8momKCV2jdGGSu6kV5H,
        _ids: {
            y: eJCW9jGsdZTD6-AD9opKwjPIOWZ4R.T0CG2kdyzf,
            x: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2,
            r: orsvTbm.vJYQS4Jw0Z-oGjcGdFFyDWp9CVj7M1CN
        }
    }
    """
    _sampleable_steps = None

    def __init__(self, *args, missing: dict = None, _sampleable=None):
        self.steps = args
        self.missing = missing or {}
        self.hasmissing = missing is not None
        self.sampleable = bool(self.sampleable_steps) if _sampleable is None else _sampleable

    @property
    def sampleable_steps(self):
        if self._sampleable_steps is None:
            self._sampleable_steps = [step for step in self.steps if step.sampleable]
        return self._sampleable_steps

    def sample(self, rnd: int | Random = None):
        if not self.sampleable:
            return self
        new = pipeline(_sampleable=False)
        new.steps = [step.sample(rnd) for step in self.sampleable_steps]
        new.missing = self.missing
        return new

    def __rrshift__(self, other):
        from hdict.frozenhdict import frozenhdict
        from hdict import hdict

        # REMINDER: 'dict' includes 'hdict', 'frozenhdict'
        if not isinstance(other, (frozenhdict, hdict)) and isinstance(other, dict):
            return hdict() >> other >> self
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other):
        from hdict import apply
        from hdict.content.applyout import applyOut

        if isinstance(other, pipeline):
            return reduce(rshift, chain(self, other))
        if isinstance(other, (applyOut, dict)):
            return pipeline(self, other, missing=self.missing)
        if isinstance(other, apply):  # pragma: no cover
            raise Exception(f"Cannot apply before specifying the output field.")
        return NotImplemented  # pragma: no cover

    def __getattr__(self, item):  # pragma: no cover
        if self.missing:
            self.show()
            raise Exception(
                f"'pipeline' has no attribute '{item}'.\n"
                f"If you are expecting a 'hdict' instead of a 'pipeline',\n"
                f"you need to provide the hdict its respective missing field '{self.missing}' before application."
            )
        return self.__getattribute__(item)

    def __repr__(self):
        return " » ".join(repr(step) for step in self)

    def show(self, colored=True, key_quotes=False):
        r"""Print textual representation of a pipeline object"""
        print(self.astext(colored, key_quotes))

    def astext(self, colored=True, key_quotes=False, extra_items=None):
        r"""
        Textual representation of a pipeline object

        >>> p = pipeline({"b":2}, {"a":1})
        >>> p
        {'b': 2} » {'a': 1}
        >>> p.show()
        {'b': 2} » {'a': 1}
        """
        from hdict.frozenhdict import frozenhdict
        from hdict import hdict

        extra_items = extra_items or {}
        if self.missing:
            if len(self.missing) != 1:  # pragma: no cover
                raise Exception(f"'missing' should have only one item.")
        out = []
        extra_items_ = extra_items.copy()
        for step in self:
            if isinstance(step, (frozenhdict, hdict)):
                delete = False
                if step.id in self.missing:
                    extra_items_[self.missing[step.id]] = "✗ first missing field ✗"
                    delete = True
                out.append(step.astext(colored=colored, key_quotes=key_quotes, extra_items=extra_items_))
                if delete:
                    del extra_items_[self.missing[step.id]]
            else:
                out.append(repr(step))
        return " » ".join(out)

    def __str__(self):
        # TODO: include 'missing' annotation like done for astext/repr?
        out = []
        for step in self:
            out.append(str(step))
        return " » ".join(out)

    def __iter__(self):
        for step in self.steps:
            if isinstance(step, pipeline):
                yield from step
            else:
                yield step
