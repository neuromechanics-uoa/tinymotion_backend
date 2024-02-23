import os
import logging
import uuid
import hashlib
from typing import Annotated

from fastapi import UploadFile, File, Form, Depends, HTTPException, APIRouter

from tinymotion_backend.core.config import settings
from tinymotion_backend import models
from tinymotion_backend.api import deps
from tinymotion_backend.services.video_service import VideoService
from tinymotion_backend.core.exc import NotFoundError, NoConsentError


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=models.VideoOut,
    responses={
        400: {
            "description": "Bad Request Error",
            "content": {"application/json": {"example": {"detail": "No consent exists"}}},
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Not authenticated"}}},
        },
        404: {
            "description": "Not Found Error",
            "content": {"application/json": {"example": {"detail": "An infant with the specified NHI number "
                                                         "does not exist"}}},
        },
        409: {
            "description": "Conflict Error",
            "content": {"application/json": {"example": {"detail": "Verification of the SHA256 checksum of the uploaded video failed"}}},
        },
    },
)
def upload_video(
    video: Annotated[UploadFile, File(description="Video file")],
    nhi_number: Annotated[str, Form(description="NHI number of the infant in the video", min_length=1)],
    checksum_sha256: Annotated[str, Form(
        description="The SHA256 checksum to verify the integrity of the uploaded video",
        min_length=64,
        max_length=64,
    ),],
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
    video_service: VideoService = Depends(deps.get_video_service),
):
    """
    Upload a video associated with an infant

    """
    # first we create a record in the db for this video
    video_name = str(uuid.uuid4()) + os.path.splitext(video.filename)[1]
    try:
        video_in = models.VideoCreateViaNHI(
            sha256sum=checksum_sha256,
            video_name=video_name,
            nhi_number=nhi_number,
        )
        video_record = video_service.create_using_nhi_number(video_in)

    except NotFoundError as exc:
        logger.error(f"Error creating video record: {exc}")
        raise HTTPException(
            status_code=404,
            detail="An infant with the specified NHI number does not exist",
        )

    except NoConsentError as exc:
        logger.error(f"Error creating video record: {exc}")
        raise HTTPException(
            status_code=400,
            detail="No consent exists",
        )

    stored_file = os.path.join(settings.VIDEO_LIBRARY_PATH, video_name)
    try:
        # next we store the video file to disk
        logger.debug(f"Storing video locally: {stored_file}")
        # TODO: write to tmpdir instead until checksum verified, then move to storage (but would have to check checksum again?)
        logger.debug(f"Receiving video: {video.filename} (size: {video.size}; content_type: {video.content_type})")
        sha256_hash = hashlib.sha256()
        with open(stored_file, "wb") as out_file:
            while content := video.file.read(settings.FILE_CHUNK_SIZE_BYTES):
                out_file.write(content)
                sha256_hash.update(content)

        # now we verify the checksum
        if checksum_sha256 != sha256_hash.hexdigest():
            logger.error(f"Checksums do not match (theirs: {checksum_sha256} ; ours: {sha256_hash.hexdigest()})")

            # delete the record in the database
            video_service.delete(video_record.video_id)
            # and delete the file
            if os.path.exists(stored_file):
                os.unlink(stored_file)

            raise HTTPException(
                status_code=409,
                detail=f"Verification of the SHA256 checksum of the uploaded video failed ({sha256_hash.hexdigest()})",
            )

        logger.debug("Finished receiving video file")

    except HTTPException:
        raise

    except Exception as exc:
        logger.error("Caught exception while writing video file, removing file and record")
        logger.error(f"Exception was: {exc!r}")
        if os.path.exists(stored_file):
            os.unlink(stored_file)
        video_service.delete(video_record.video_id)
        raise

    # TODO: option to use object storage?

    return video_record
