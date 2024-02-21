

class TinyMotionException(Exception):
    """
    Base exception class

    """
    pass


class UniqueConstraintError(TinyMotionException):
    """
    Error due to not honouring a unique constraint

    """
    pass
