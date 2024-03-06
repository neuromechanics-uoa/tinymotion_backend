import os
import typer
from typing import Annotated
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.video_service import VideoService
from tinymotion_backend.core.config import settings


app = typer.Typer()


@app.command()
def list_videos():
    """
    List stored videos.

    """
    with Session(database.engine) as session:
        video_service = VideoService(session, 0)
        videos = video_service.list()
        print(f"Found {len(videos)} videos")
        for video in videos:
            print(repr(video))


@app.command()
def delete_video(
    video_id: Annotated[int, typer.Argument(help="The video id of the video to delete", default=None)],
):
    """
    Delete the specified video and the associated record in the database.

    """
    with Session(database.engine) as session:
        video_service = VideoService(session, 0)

        # first get the video and confirm deletion
        video_record = video_service.get(video_id)
        print(f"Deleting {video_record!r}")
        video_path = os.path.join(settings.VIDEO_LIBRARY_PATH, video_record.video_name)
        print(f"Video file path: {video_path}")
        if not os.path.exists(video_path):
            raise RuntimeError(f"Cannot find video file to delete ({video_path})")

        delete = typer.confirm("Are you sure you want to delete it?")
        if not delete:
            print("Not deleting")
            raise typer.Abort()

        else:
            # delete the video
            video_service.delete(video_id)
            os.unlink(video_path)
