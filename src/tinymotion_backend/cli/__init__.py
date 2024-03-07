import click

from tinymotion_backend._version import __version__
from tinymotion_backend.cli.users import users
from tinymotion_backend.cli.videos import videos


@click.group(name="tinymotion-backend")
def cli():
    """Command line interface to TinyMotion Backend"""
    pass


cli.add_command(users)
cli.add_command(videos)


@cli.command()
def version():
    """Print the version of the TinyMotion backend and exit."""
    print(f"TinyMotion Backend v{__version__}")
