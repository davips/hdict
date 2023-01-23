from hdict.entry.field import field
from hdict.entry.apply import apply
from hdict.entry.sample import sample
from hdict.entry.value import value
from hdict.hdict_ import hdict


class _:
    def __call__(self, *args, **kwargs):
        return apply(*args, **kwargs)

    def __getattr__(self, item):
        return field(item)

    def __getitem__(self, item):
        return sample(item)
