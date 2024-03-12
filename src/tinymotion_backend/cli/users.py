import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.models import UserCreate, UserUpdate


@click.group()
def users():
    """Commands to interact with users in the backend."""
    pass


@users.command()
@click.option('-e', '--email', required=True, type=str, help="The new user's email")
@click.option('-k', '--access-key', required=True, type=str, help="The new user's access key that they will use to login")
@click.option('-d', '--disabled', is_flag=True, default=False, show_default=True, help="Disable the user's account on creation")
def create(
    email: str,
    access_key: str,
    disabled: bool,
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


@users.command()
@click.argument('user_id', type=click.INT)
@click.option('-e', '--email', required=False, default=None, type=str, help="Update the user's email")
@click.option('-k', '--access-key', required=False, default=None, type=str, help="Update the user's access key")
@click.option('-d', '--disabled', required=False, default=None, type=bool, help="Update whether the user is disabled")
def update(
    user_id: int,
    email: str | None,
    access_key: str | None,
    disabled: bool | None,
):
    """Update the specified User.

    USER_ID is the id of the user to update.
    """
    with Session(database.engine) as session:
        user_service = UserService(session)

        update_obj = UserUpdate(
            email=email,
            access_key=access_key,
            disabled=disabled,
        )
        updated_user = user_service.update(user_id, update_obj)

        click.echo(f"Updated user: {updated_user!r}")


@users.command()
@click.argument('user_id', type=click.INT)
def delete(
    user_id: int,
):
    """Delete the specified User.

    USER_ID is the id of the user to delete.
    """
    with Session(database.engine) as session:
        user_service = UserService(session)

        # first get the user and confirm deletion
        user_record = user_service.get(user_id)
        click.echo(f"Deleting {user_record!r}")
        delete = click.confirm("Are you sure you want to delete it?")
        if not delete:
            click.echo("Not deleting")
            raise click.Abort()
        else:
            # delete the user
            user_service.delete(user_id)
