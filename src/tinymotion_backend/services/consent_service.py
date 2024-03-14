import logging

from sqlmodel import Session

from tinymotion_backend.services.base import BaseService
from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.models import Consent, ConsentCreate, ConsentUpdate, ConsentCreateViaNHI
from tinymotion_backend.core.exc import InvalidInputError


logger = logging.getLogger(__name__)


class ConsentService(BaseService[Consent, ConsentCreate, ConsentUpdate]):
    def __init__(self, db_session: Session, created_by: int):
        super(ConsentService, self).__init__(Consent, db_session, created_by=created_by)

    def create(self, obj: ConsentCreate) -> Consent:
        """
        Override create to first validate the incoming data.

        - If `collected_physically` is set, the other fields are not set
        - If `collected_physically` is not set, the other fields must be set

        """
        if obj.collected_physically:
            # TODO: maybe it doesn't matter what else is set...
            pass

        else:
            if obj.consent_giver_email is None:
                msg = "Must set `consent_giver_email` when not specifying `collected_physically`"
                logger.error(msg)
                raise InvalidInputError(msg)

            if obj.consent_giver_name is None:
                msg = "Must set `consent_giver_name` when not specifying `collected_physically`"
                logger.error(msg)
                raise InvalidInputError(msg)

        # TODO: send email?

        return super(ConsentService, self).create(obj)

    def create_using_nhi_number(self, obj: ConsentCreateViaNHI) -> Consent:
        """Create consent using the NHI number to identify the Infant"""
        # get the Infant
        infant_service = InfantService(self.db_session, self.created_by)
        infant = infant_service.get_by_nhi_number(obj.nhi_number)

        # now create the consent
        consent_obj = ConsentCreate(
            infant_id=infant.infant_id,
            consent_giver_name=obj.consent_giver_name,
            consent_giver_email=obj.consent_giver_email,
            collected_physically=obj.collected_physically,
        )
        created_consent = self.create(consent_obj)

        return created_consent
