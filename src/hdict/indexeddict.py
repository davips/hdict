from indexed import IndexedOrderedDict


class IndexedDict(IndexedOrderedDict):
    """
    Wrapper with a cleaner representation of IndexedOrderedDict.

    >>> IndexedDict([('a', 'a'), ('b', 'b')])
    {'a': 'a', 'b': 'b'}
    """

    def __repr__(self):
        return repr(dict(self.items()))
