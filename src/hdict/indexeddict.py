from indexed import IndexedOrderedDict


class IndexedDict(IndexedOrderedDict):
    """
    >>> IndexedDict([('a', 'a'), ('b', 'b')])
    {'a': 'a', 'b': 'b'}
    """

    def __repr__(self):
        return repr(dict(self.items()))
