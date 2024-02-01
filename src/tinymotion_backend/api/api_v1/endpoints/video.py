import os
import uuid
import hashlib
from typing import Annotated
from dataclasses import dataclass
import datetime

from pydantic import BaseModel
from fastapi import UploadFile, File, Form, Depends, HTTPException, APIRouter

from tinymotion_backend.core.config import settings
from tinymotion_backend import models
from tinymotion_backend.api import deps

router = APIRouter()


class ErrorMessage(BaseModel):
    detail: str


class UploadVideoResponse(BaseModel):
    video_id: str
# TODO: video_id and possibly msg instead


@dataclass
class VideoMetadata:
    full_name: Annotated[str, Form(
        min_length=1,
        description="Child's full name",
    )]
    nhi_number: Annotated[str, Form(
        min_length=1,
        description="NHI number associated with the video",
    )]
    birth_date: Annotated[datetime.date, Form(
        description="Child's birth date associated with the video",
    )]
    due_date: Annotated[datetime.date, Form(
        description="Mother's due date associated with the video",
    )]
    consent_name: Annotated[str, Form(
        min_length=1,
        description="Name of the parent or caregiver "
                    "giving consent for the video",
    )]
    sha256sum: Annotated[str, Form(
        min_length=64,
        max_length=64,
        description="SHA256 checksum to verify the checksum of the "
                    "uploaded file against"
    )]


@router.post("/", responses={409: {"model": ErrorMessage}, 401: {"model": ErrorMessage}}, response_model=UploadVideoResponse)
def upload_video(
    video: Annotated[UploadFile, File(description="Video file")],  # metadata: VideoMetadata = Depends(),
    metadata: Annotated[VideoMetadata, Depends()],
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
):
    """
    Upload a video and associated metadata.

    """
    # store the video file to disk
    # TODO: write to tmpdir instead?
    print(f"Receiving video: {video.filename} (size: {video.size}; content_type: {video.content_type})")
    sha256_hash = hashlib.sha256()
    video_id = str(uuid.uuid4())
    stored_file = f"{video_id}_{video.filename}"
    with aiofiles.open(stored_file, "wb") as out_file:
        while content := video.read(settings.FILE_CHUNK_SIZE_BYTES):
            out_file.write(content)
            sha256_hash.update(content)

    # compare checksum
    if metadata.sha256sum != sha256_hash.hexdigest():
        raise HTTPException(
            status_code=409,
            detail=f"Verification of the checksum for the uploaded video file failed ({sha256_hash.hexdigest()})",
        )

    # push to object storage (async??)

    # delete the file
    os.unlink(stored_file)

    return UploadVideoResponse(video_id=video_id)
