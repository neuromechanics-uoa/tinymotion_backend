import uuid
import json

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.models import UserCreate, UserUpdate
from tinymotion_backend.cli.utils import convert_json


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
    click.echo(user_added.model_dump_json(indent=2))


@user.command()
@click.option("-p", "--pager", is_flag=True, default=False, help="Display results using a pager")
@click.option("-o", "--output-file", type=str, required=False, default=None, help="Write JSON output to file")
@click.option("-q", "--quiet", is_flag=True, default=False, help="Don't write Infants to standard output")
def list(pager: bool, output_file: str, quiet: bool):
    """List existing users."""
    with Session(database.engine) as session:
        # get the list of Users
        user_service = UserService(session)
        users = user_service.list()
        click.echo(f"Found {len(users)} Users")

        # build a list of Users in json format
        users_json = []
        for user in users:
            users_json.append(json.loads(user.json()))

        if not quiet:
            # display to screen with pager or not
            if pager:
                echo_command = click.echo_via_pager
            else:
                echo_command = click.echo

            # print to screen
            echo_command(json.dumps(users_json, indent=2, default=convert_json))

        # write json to file if requested
        if output_file is not None:
            with open(output_file, "w") as fout:
                fout.write(json.dumps(users_json, indent=2))
            click.echo(f"Written Users to {output_file}")


@user.command()
@click.argument('user_id', type=click.UUID)
@click.option('-e', '--email', required=False, default=None, type=str, help="Update the user's email")
@click.option('-k', '--access-key', required=False, default=None, type=str, help="Update the user's access key")
@click.option('-d', '--disabled', required=False, default=None, type=bool, help="Update whether the user is disabled")
@click.pass_context
def update(
    ctx: click.Context,
    user_id: uuid.UUID,
    email: str | None,
    access_key: str | None,
    disabled: bool | None,
):
    """Update the specified User.

    USER_ID is the id of the user to update.
    """
    # only update values that were passed, ignore those that are defaults
    update_obj_dict = {}
    if ctx.get_parameter_source("email").name != "DEFAULT":
        update_obj_dict["email"] = email
    if ctx.get_parameter_source("access_key").name != "DEFAULT":
        update_obj_dict["access_key"] = access_key
    if ctx.get_parameter_source("disabled").name != "DEFAULT":
        update_obj_dict["disabled"] = disabled

    # validate passed in values
    update_obj = UserUpdate.model_validate(update_obj_dict)

    # now update the stored record
    with Session(database.engine) as session:
        user_service = UserService(session)
        updated_user = user_service.update(user_id, update_obj)

        click.echo("Updated user:")
        click.echo(updated_user.model_dump_json(indent=2))


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
        click.echo(user_record.model_dump_json(indent=2))
        delete = click.confirm("Are you sure you want to delete it?")
        if not delete:
            click.echo("Not deleting")
            raise click.Abort()
        else:
            # delete the user
            user_service.delete(user_id)
            print("Deleted user.")
