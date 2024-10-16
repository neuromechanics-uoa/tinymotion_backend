import json
import uuid
import datetime

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.models import InfantCreate, InfantUpdate
from tinymotion_backend.cli.utils import check_user_id, convert_json


@click.group()
def infant():
    """Commands to interact with infants in the backend."""
    pass


@infant.command()
@click.option("-u", "--user-id", required=True, type=click.UUID, help="ID of the User to create the Infant")
@click.option('-f', '--full-name', required=True, type=str, help="The infant's full name")
@click.option('-n', '--nhi-number', required=True, type=str, help="The infant's NHI number")
@click.option('-b', '--birth-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]),
              help="The infant's date of birth")
@click.option('-d', '--due-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]),
              help="The infant's expected date of birth")
def create(
    user_id: uuid.UUID,
    full_name: str,
    nhi_number: str,
    birth_date: datetime.datetime,
    due_date: datetime.datetime,
):
    """Create a new infant."""
    # check valid user id
    check_user_id(user_id)

    # preparing to create the infant
    new_infant = InfantCreate(
        full_name=full_name,
        nhi_number=nhi_number,
        birth_date=birth_date.date(),
        due_date=due_date.date(),
    )

    # create the infant
    with Session(database.engine) as session:
        infant_service = InfantService(session, user_id)
        infant_added = infant_service.create(new_infant)

    click.echo("Successfully created new infant:")
    click.echo(infant_added.model_dump_json(indent=2))


@infant.command()
@click.option("-p", "--pager", is_flag=True, default=False, help="Display results using a pager")
@click.option("-j", "--json-output", is_flag=True, default=False, help="Output JSON only, no extra messages")
def list(pager: bool, json_output: bool):
    """List existing infants."""
    with Session(database.engine) as session:
        # get the list of Infants
        infant_service = InfantService(session, None)
        infants = infant_service.list()
        if not json_output:
            click.echo(f"Found {len(infants)} Infants")

        # build a list of Infants in json format
        infants_json = []
        for infant in infants:
            infants_json.append(json.loads(infant.json()))

        # display to screen with pager or not
        if pager and not json_output:
            echo_command = click.echo_via_pager
        else:
            echo_command = click.echo

        echo_command(json.dumps(infants_json, indent=2, default=convert_json))


@infant.command()
@click.argument('infant_id', type=click.UUID)
@click.option('-f', '--full-name', required=False, default=None, type=str, help="The infant's full name")
@click.option('-n', '--nhi-number', required=False, default=None, type=str, help="The infant's NHI number")
@click.option('-b', '--birth-date', required=False, default=None, type=click.DateTime(formats=["%Y-%m-%d"]),
              help="The infant's date of birth")
@click.option('-d', '--due-date', required=False, default=None, type=click.DateTime(formats=["%Y-%m-%d"]),
              help="The infant's expected date of birth")
@click.pass_context
def update(
    ctx: click.Context,
    infant_id: uuid.UUID,
    full_name: str | None,
    nhi_number: str | None,
    birth_date: datetime.datetime | None,
    due_date: datetime.datetime | None,
):
    """Update the specified Infant.

    INFANT_ID is the id of the infant to update.
    """
    update_infant_dict = {}
    if ctx.get_parameter_source("full_name").name != "DEFAULT":
        update_infant_dict["full_name"] = full_name
    if ctx.get_parameter_source("nhi_number").name != "DEFAULT":
        update_infant_dict["nhi_number"] = nhi_number
    if ctx.get_parameter_source("birth_date").name != "DEFAULT":
        update_infant_dict["birth_date"] = birth_date.date()
    if ctx.get_parameter_source("due_date").name != "DEFAULT":
        update_infant_dict["due_date"] = due_date.date()

    # validate passed in values
    update_obj = InfantUpdate.model_validate(update_infant_dict)

    with Session(database.engine) as session:
        infant_service = InfantService(session, 0)
        updated_infant = infant_service.update(infant_id, update_obj)

        click.echo("Updated infant")
        click.echo(updated_infant.model_dump_json(indent=2))


@infant.command()
@click.argument('infant_id', type=click.UUID)
def delete(
    infant_id: uuid.UUID,
):
    """Delete the specified Infant.

    INFANT_ID is the id of the infant to delete.
    """
    with Session(database.engine) as session:
        infant_service = InfantService(session, None)

        click.echo(f"Infant id: {infant_id} ({type(infant_id)})")

        # first get the infant and confirm deletion
        infant_record = infant_service.get(infant_id)
        click.echo("Deleting infant:")
        click.echo(infant_record.model_dump_json(indent=2))
        click.echo(f"Also deleting {len(infant_record.consents)} consent(s) and "
                   f"{len(infant_record.videos)} video(s) associated with this infant.")
        delete = click.confirm("Do you wish to proceed?")
        if not delete:
            click.echo("Not deleting")
            raise click.Abort()
        else:
            # delete the infant
            infant_service.delete(infant_id)
            print("Deleted infant.")
