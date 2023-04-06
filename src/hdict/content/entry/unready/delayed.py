from dataclasses import dataclass

from hdict.content.argument import AbsBaseArgument
from hdict.content.argument.sample import sample
from hdict.content.entry.unready import AbsUnreadyEntry


@dataclass
class DelayedEntry(AbsUnreadyEntry):
    """
    Wrapper for an entry currently dependent on missing fields to be ready
    """
    argument: AbsBaseArgument | sample

    def __repr__(self):
        return f"✗ delayed: {self.argument}"


@dataclass
class DelayedMultiEntry(AbsUnreadyEntry):
    """
    Wrapper for an entry currently dependent on missing fields to be ready
    """
    keys: tuple
    argument: AbsBaseArgument | sample
    fields: list

    def __repr__(self):
        return f"✗ delayed: ({','.join(self.fields)}) = {self.argument}"
