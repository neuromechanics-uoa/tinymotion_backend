import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.models import UserCreate


@click.group()
def users():
    """Commands to interact with users in the backend."""
    pass


@users.command()
@click.option('-e', '--email', required=True, help="The new user's email")
@click.option('-k', '--access-key', required=True, help="The new user's access key that they will use to login")
@click.option('-d', '--disabled', required=True, help="Disable the user's account on creation")
def create(
    email,
    access_key,
    disabled,
):
    """Create a new user."""
    new_user = UserCreate(
        email=email,
        access_key=access_key,
        disabled=disabled,
    )

    with Session(database.engine) as session:
        user_service = UserService(session)
        user_added = user_service.create(new_user)

    click.echo(f"Successfully added new user: {user_added!r}")


@users.command()
def list():
    """List existing users."""
    with Session(database.engine) as session:
        user_service = UserService(session)
        users = user_service.list()
        click.echo(f"Found {len(users)} users")
        for user in users:
            click.echo(repr(user))
