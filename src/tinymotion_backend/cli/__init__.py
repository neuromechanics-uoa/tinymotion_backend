import click

from tinymotion_backend._version import __version__
from tinymotion_backend.cli.consents import consent
from tinymotion_backend.cli.infants import infant
from tinymotion_backend.cli.secret import secret
from tinymotion_backend.cli.users import user
from tinymotion_backend.cli.videos import video


@click.group(name="tinymotion-backend")
def cli():
    """Command line interface to TinyMotion Backend"""
    pass


cli.add_command(consent)
cli.add_command(infant)
cli.add_command(secret)
cli.add_command(user)
cli.add_command(video)


@cli.command()
def version():
    """Print the version of the TinyMotion backend and exit."""
    print(f"TinyMotion Backend v{__version__}")
