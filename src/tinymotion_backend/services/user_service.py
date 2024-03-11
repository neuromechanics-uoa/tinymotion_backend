import logging
from typing import Optional

from sqlmodel import select, Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from tinymotion_backend.services.base import BaseService
from tinymotion_backend.models import User, UserCreate, UserUpdate, UserRead
from tinymotion_backend.core.exc import InvalidAccessKeyError, UniqueConstraintError


logger = logging.getLogger(__name__)


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, db_session: Session):
        super(UserService, self).__init__(User, db_session)

    def get_by_access_key(self, access_key: str) -> Optional[UserRead]:
        """
        Get User by access key

        """
        try:
            user = self.db_session.exec(
                select(User).where(User.access_key == access_key)
            ).one()
        except NoResultFound:
            logger.error("Could not find any user with the given access key")
            raise InvalidAccessKeyError("Could not find any user with the given access key")
        except MultipleResultsFound:
            logger.error("Found multiple users with the given access key")
            raise UniqueConstraintError("Found multiple users with the given access key")

        return user

    def authenticate(self, access_key: str) -> Optional[UserRead]:
        return self.get_by_access_key(access_key)

    def is_disabled(self, user: User) -> bool:
        return user.disabled
