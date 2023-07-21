from random import Random

from hdict.abs import AbsAny


class AbsArgument(AbsAny):
    """
    Argument provided by the user alongside the applied function

    For classes where sampling makes no sense, return the object itself.
    """

    sampleable = False

    def sample(self, rnd: int | Random = None):
        return self


class AbsBaseArgument(AbsArgument):
    """
    Normal function argument provided by the user: `value`*, `field`, `apply`; or from advanced use: `entry`

    Exceptionally, 'field' is a subclass that can also be piped through '>>'
    *value also inherits AbsBaseArgument
    """


class AbsMetaArgument(AbsArgument):
    """
    Special temporary argument-like directive provided by the user: `default`, `sample`
    """
