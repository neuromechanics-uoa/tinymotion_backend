import logging
from typing import Optional

from sqlmodel import select, Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from tinymotion_backend.services.base import BaseService
from tinymotion_backend.models import Infant, InfantCreate, InfantUpdate


logger = logging.getLogger(__name__)


class InfantService(BaseService[Infant, InfantCreate, InfantUpdate]):
    def __init__(self, db_session: Session):
        super(InfantService, self).__init__(Infant, db_session)

    def get_by_nhi_number(self, nhi_number: str) -> Optional[Infant]:
        """
        Get Infant by NHI number

        """
        try:
            infant = self.db_session.exec(
                select(Infant).where(Infant.nhi_number == nhi_number)
            ).one()
        except NoResultFound:
            logger.error("Could not find any infant with the given NHI number")
            infant = None
        except MultipleResultsFound:
            logger.error("Found multiple infants with the given NHI number")
            infant = None

        return infant
