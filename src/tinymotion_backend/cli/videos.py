import os

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.video_service import VideoService
from tinymotion_backend.core.config import settings


@click.group()
def videos():
    """Commands to interact with videos in the backend."""
    pass


@videos.command()
def list():
    """List stored videos."""
    with Session(database.engine) as session:
        video_service = VideoService(session, 0)
        videos = video_service.list()
        click.echo(f"Found {len(videos)} videos")
        for video in videos:
            click.echo(repr(video))


@videos.command()
@click.argument('video_id', type=click.INT)
def delete(
    video_id: int,
):
    """Delete the specified video and the associated record in the database.

    VIDEO_ID is the id of of the video to delete.
    """
    with Session(database.engine) as session:
        video_service = VideoService(session, 0)

        # first get the video and confirm deletion
        video_record = video_service.get(video_id)
        click.echo(f"Deleting {video_record!r}")
        video_path = os.path.join(settings.VIDEO_LIBRARY_PATH, video_record.video_name)
        click.echo(f"Video file path: {video_path}")
        if not os.path.exists(video_path):
            raise RuntimeError(f"Cannot find video file to delete ({video_path})")

        delete = click.confirm("Are you sure you want to delete it?")
        if not delete:
            click.echo("Not deleting")
            raise click.Abort()

        else:
            # delete the video
            video_service.delete(video_id)
            os.unlink(video_path)
