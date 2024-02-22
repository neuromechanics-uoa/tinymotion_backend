

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


class NotFoundError(TinyMotionException):
    """
    Error due to some object not being found in the database

    """


class InvalidInputError(TinyMotionException):
    """Input data is not valid"""
