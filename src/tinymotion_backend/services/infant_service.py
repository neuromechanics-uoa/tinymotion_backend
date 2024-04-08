import logging
import uuid

from sqlmodel import select, Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from tinymotion_backend.services.base import BaseService
from tinymotion_backend.models import Infant, InfantCreate, InfantUpdate
from tinymotion_backend.core.exc import NotFoundError, UniqueConstraintError


logger = logging.getLogger(__name__)


class InfantService(BaseService[Infant, InfantCreate, InfantUpdate]):
    def __init__(self, db_session: Session, created_by: uuid.UUID):
        super(InfantService, self).__init__(Infant, db_session, created_by=created_by)

    def get_by_nhi_number(self, nhi_number: str) -> Infant:
        """
        Get Infant by NHI number

        """
        try:
            infant = self.db_session.exec(
                select(Infant).where(Infant.nhi_number == nhi_number)
            ).one()
        except NoResultFound:
            logger.error("Could not find any infant with the given NHI number")
            raise NotFoundError("Could not find any infant with the given NHI number")
        except MultipleResultsFound:
            logger.error("Found multiple infants with the given NHI number")
            raise UniqueConstraintError("Found multiple infants with the given NHI number")

        return infant
