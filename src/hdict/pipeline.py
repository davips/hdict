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
from random import Random

from hdict.content.abs.abssampleable import AbsSampleable


class pipeline(AbsSampleable):
    def __init__(self, *args, missing=None):
        self.steps = args
        self.missing = missing
        self.hasmissing = missing is not None

    def sample(self, rnd: int | Random = None):
        new = pipeline()
        new.steps = [(step.sample(rnd) if isinstance(step, AbsSampleable) else step) for step in self.steps]
        new.missing = self.missing
        return new

    def __rrshift__(self, other):
        from hdict.content.applyout import applyOut
        if not isinstance(other, pipeline) and isinstance(other, (applyOut, dict)):  # 'dict' includes 'hdict', 'frozenhdict'
            # REMINDER: all combinations of steps are valid pipelines
            return pipeline(other, self.clean).apply()
        return NotImplemented  # pragma: no cover

    @property
    def clean(self):
        new = pipeline()
        new.steps = self.steps
        return new

    def __rshift__(self, other):
        from hdict import apply
        from hdict.content.applyout import applyOut
        if isinstance(other, pipeline):
            return pipeline(self.clean, other.clean, missing=self.missing).apply()
        if isinstance(other, (applyOut, dict)):
            return pipeline(self, other, missing=self.missing)
        if isinstance(other, apply):  # pragma: no cover
            raise Exception(f"Cannot apply before specifying the output field.")
        return NotImplemented  # pragma: no cover

    def __getattr__(self, item):
        mudar
        if self.missing is not None:  # pragma: no cover
            raise Exception(f"'pipeline' has no attribute '{item}'.\n"
                            f"If you are expecting a 'hdict' instead of a 'pipeline',\n"
                            f"you need to provide the missing field '{self.missing}' before application.")
        return self.__getattribute__(item)  # pragma: no cover

    def __repr__(self):
        return " » ".join(repr(step) for step in self.steps)

    def show(self, colored=True, key_quotes=False):
        r"""Print textual representation of a pipeline object"""
        print(self.astext(colored, key_quotes))

    def astext(self, colored=True, key_quotes=False, extra_items=None):
        r"""Textual representation of a pipeline object"""
        if self.missing and not extra_items:
            extra_items = {self.missing: "✗ missing ✗"}
        out = []
        for step in self.steps:
            if hasattr(step, "astext"):
                out.append(step.astext(colored=colored, key_quotes=key_quotes, extra_items=extra_items))
            else:
                out.append(repr(step))
        return " » ".join(out)

    def __str__(self):
        # TODO: include 'missing' annotation like done for astext/repr?
        out = []
        for step in self.steps:
            out.append(str(step))
        return " » ".join(out)

    def apply(self):
        """
        Solve a complete pipeline, resulting in a hdict/frozenhdict

        Not intended to be called directly as providing the missing field will result in the expected hdict/frozenhdict

        >>> from hdict import _
        >>> p = _(x=5) >> _(lambda x, y: x + y).r
        >>> p.show(colored=False)
        {
            x: 5,
            _id: PRj.5PqNWuPfNvmXl83el.sSMPcTS02ZIl4.K.5k,
            _ids: {
                x: ecvgo-CBPi7wRWIxNzuo1HgHQCbdvR058xi6zmr2
            },
            y: ✗ missing ✗
        } » r=λ(x y)
        >>> p2 = _(y=7) >> p
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
        """
        from hdict.hdict_ import hdict
        from hdict.frozenhdict import frozenhdict
        if self.missing is not None:  # pragma: no cover
            raise Exception(f"Cannot apply a pipeline before providing the missing field '{self.missing}'.")
        if isinstance(self.steps[0], dict) and not isinstance(self.steps[0], (hdict, frozenhdict)):
            raise Exception(f"Cannot apply a pipeline started by a 'dict'. It is incomplete.")  # pragma: no cover
        result = NoOp
        missing = []
        for step in self:
            result >>= step
            if isinstance(result, pipeline) and result.missing is not None:
                # REMINDER: '{"y": 4} >> hdict()' is necessarily a pipeline.
                #   Reason: dicts are intended to provide application as well 'hdict() >> {"y": 4, "z": _(f)}'
                #           and can't depend on futures values (those to the right of '>>').
                missing.append(result.missing)
        if missing:#TODO: remove exception
            self.show()
            msg = f"Cannot apply incomplete pipeline.\n" \
                  f"Missing fields: '{missing}'.\n" \
                  f"The fields should appear before application in the pipeline."
            raise Exception(msg)
        return result

    def evaluate(self):
        result = self.apply()
        # result.evaluate()

    def __iter__(self):
        for step in self.steps:
            if isinstance(step, pipeline):
                yield from step
            else:
                yield step


class NoOp:
    def __rshift__(self, other):
        return other


NoOp = NoOp()
