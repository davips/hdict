from hdict.content.entry.unready import AbsUnreadyEntry


class MissingEntry(AbsUnreadyEntry):
    """
    Placeholder for a missing field
    """

    def __repr__(self):
        return "✗ missing"
