import os
import logging
import uuid

from sqlmodel import select, Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from tinymotion_backend.services.base import BaseService
from tinymotion_backend.models import Infant, InfantCreate, InfantUpdate
from tinymotion_backend.core.exc import NotFoundError, UniqueConstraintError
from tinymotion_backend.core.config import settings


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

    def delete(self, infant_id: uuid.UUID) -> None:
        """Delete the infant including video files"""
        logger.debug(f"Deleting infant: {infant_id}")

        # first list all video files belonging to this infant
        db_obj = self.get(infant_id)
        logger.debug(f"Infant has {len(db_obj.consents)} consents and {len(db_obj.videos)} videos")
        infant_videos = [video.video_name for video in db_obj.videos]

        # delete the infant (and all consent and video records) from the database
        self.db_session.delete(db_obj)
        self.db_session.commit()

        # delete the video files too
        for video_name in infant_videos:
            video_path = os.path.join(settings.VIDEO_LIBRARY_PATH, video_name)
            if os.path.exists(video_path):
                logger.debug(f"Deleting video: {video_path}")
                os.unlink(video_path)
            else:
                logger.error(f"Could not delete video file: {video_path} (file does not exist)")
