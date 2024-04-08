import uuid
import json

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.models import UserCreate, UserUpdate


@click.group()
def user():
    """Commands to interact with users in the backend."""
    pass


@user.command()
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

    click.echo("Successfully created new user:")
    click.echo(json.dumps(json.loads(user_added.json()), indent=2))


@user.command()
@click.option("-p", "--pager", is_flag=True, default=False, help="Display results using a pager")
def list(pager: bool):
    """List existing users."""
    with Session(database.engine) as session:
        user_service = UserService(session)
        users = user_service.list()
        click.echo(f"Found {len(users)} users:")
        users_json = []
        for user in users:
            users_json.append(json.loads(user.json()))
        if pager:
            echo_command = click.echo_via_pager
        else:
            echo_command = click.echo
        echo_command(json.dumps(users_json, indent=2))


@user.command()
@click.argument('user_id', type=click.UUID)
@click.option('-e', '--email', required=False, default=None, type=str, help="Update the user's email")
@click.option('-k', '--access-key', required=False, default=None, type=str, help="Update the user's access key")
@click.option('-d', '--disabled', required=False, default=None, type=bool, help="Update whether the user is disabled")
def update(
    user_id: uuid.UUID,
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

        click.echo("Updated user:")
        click.echo(json.dumps(json.loads(updated_user.json()), indent=2))


@user.command()
@click.argument('user_id', type=click.UUID)
def delete(
    user_id: uuid.UUID,
):
    """Delete the specified User.

    USER_ID is the id of the user to delete.
    """
    with Session(database.engine) as session:
        user_service = UserService(session)

        # first get the user and confirm deletion
        user_record = user_service.get(user_id)
        click.echo("Deleting user:")
        click.echo(json.dumps(json.loads(user_record.json()), indent=2))
        delete = click.confirm("Are you sure you want to delete it?")
        if not delete:
            click.echo("Not deleting")
            raise click.Abort()
        else:
            # delete the user
            user_service.delete(user_id)
            print("Deleted user.")
