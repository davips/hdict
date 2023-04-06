from dataclasses import dataclass

from hdict.content.argument.apply import apply
from hdict.content.argument.sample import sample
from hdict.content.entry.unready import AbsUnreadyEntry


@dataclass
class UnsampledEntry(AbsUnreadyEntry):
    """
    Wrapper for an entry in need of sampling to be ready
    """
    argument: apply | sample
