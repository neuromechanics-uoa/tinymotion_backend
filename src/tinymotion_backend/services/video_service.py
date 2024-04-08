import logging
import uuid

from sqlmodel import Session

from tinymotion_backend.services.base import BaseService
from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.models import Video, VideoCreate, VideoUpdate, VideoCreateViaNHI
from tinymotion_backend.core.exc import NoConsentError


logger = logging.getLogger(__name__)


class VideoService(BaseService[Video, VideoCreate, VideoUpdate]):
    def __init__(self, db_session: Session, created_by: uuid.UUID):
        super(VideoService, self).__init__(Video, db_session, created_by=created_by)
        self._infant_service = InfantService(db_session, created_by)

    def create(self, obj: VideoCreate) -> Video:
        # TODO: override to push to object storage, send email etc

        # check that at least one consent exists for the infant
        infant = self._infant_service.get(obj.infant_id)
        if not len(infant.consents):
            logger.error("No consent exists for this infant - cannot create video")
            raise NoConsentError("No consents exist for the infant")

        return super(VideoService, self).create(obj)

    def create_using_nhi_number(self, obj: VideoCreateViaNHI) -> Video:
        """Create video using the NHI number to identify the Infant"""
        # get the Infant
        infant = self._infant_service.get_by_nhi_number(obj.nhi_number)

        # now create the video
        video_obj: VideoCreate = VideoCreate(
            infant_id=infant.infant_id,
            video_name=obj.video_name,
            sha256sum=obj.sha256sum,
        )
        created_video = self.create(video_obj)

        return created_video
