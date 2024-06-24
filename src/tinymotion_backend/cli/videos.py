import os
import uuid
import json

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.video_service import VideoService
from tinymotion_backend.core.config import settings


@click.group()
def video():
    """Commands to interact with videos in the backend."""
    pass


@video.command()
@click.option("-p", "--pager", is_flag=True, default=False, help="Display results using a pager")
@click.option("-o", "--output-file", type=str, required=False, default=None, help="Write JSON output to file")
@click.option("-q", "--quiet", is_flag=True, default=False, help="Don't write Infants to standard output")
def list(pager: bool, output_file: str, quiet: bool):
    """List stored videos."""
    with Session(database.engine) as session:
        # get the list of Videos
        video_service = VideoService(session, 0)
        videos = video_service.list()
        click.echo(f"Found {len(videos)} Videos")

        # build a list of Videos in json format
        videos_json = []
        for video in videos:
            videos_json.append(json.loads(video.json()))

        if not quiet:
            # display to screen with pager or not
            if pager:
                echo_command = click.echo_via_pager
            else:
                echo_command = click.echo

            # print to screen
            echo_command(json.dumps(videos_json, indent=2))

        # write json to file if requested
        if output_file is not None:
            with open(output_file, "w") as fout:
                fout.write(json.dumps(videos_json, indent=2))
            click.echo(f"Written Videos data to {output_file}")


@video.command()
@click.argument('video_id', type=click.UUID)
def delete(
    video_id: uuid.UUID,
):
    """Delete the specified video and the associated record in the database.

    VIDEO_ID is the id of the video to delete.
    """
    with Session(database.engine) as session:
        video_service = VideoService(session, 0)

        # first get the video and confirm deletion
        video_record = video_service.get(video_id)
        click.echo("Deleting video:")
        click.echo(json.dumps(json.loads(video_record.json()), indent=2))
        video_path = os.path.join(settings.VIDEO_LIBRARY_PATH, video_record.video_name)
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
