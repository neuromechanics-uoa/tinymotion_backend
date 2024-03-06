import typer

from tinymotion_backend._version import __version__
from tinymotion_backend.cli.users import app as users_app
from tinymotion_backend.cli.videos import app as videos_app


app = typer.Typer()


@app.command()
def version():
    """
    Print the version of the TinyMotion backend and exit.

    """
    print(f"TinyMotionBackend v{__version__}")


app.registered_commands += users_app.registered_commands
app.registered_commands += videos_app.registered_commands
