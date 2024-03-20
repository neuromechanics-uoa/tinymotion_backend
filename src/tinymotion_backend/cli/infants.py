import datetime

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.models import InfantCreate, InfantUpdate
from tinymotion_backend.cli.utils import check_user_id


@click.group()
def infant():
    """Commands to interact with infants in the backend."""
    pass


@infant.command()
@click.option("-u", "--user-id", required=True, type=int, help="ID of the User to create the Infant")
@click.option('-f', '--full-name', required=True, type=str, help="The infant's full name")
@click.option('-n', '--nhi-number', required=True, type=str, help="The infant's NHI number")
@click.option('-b', '--birth-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]),
              help="The infant's date of birth")
@click.option('-d', '--due-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]),
              help="The infant's expected date of birth")
def create(
    user_id: int,
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

    click.echo(f"Successfully added new infant: {infant_added!r}")


@infant.command()
def list():
    """List existing infants."""
    with Session(database.engine) as session:
        infant_service = InfantService(session, 0)
        infants = infant_service.list()
        click.echo(f"Found {len(infants)} infants")
        for infant in infants:
            click.echo(repr(infant))


#@infant.command()
#@click.argument('infant_id', type=click.INT)
#@click.option('-f', '--full-name', required=False, default=None, type=str, help="The infant's full name")
#@click.option('-n', '--nhi-number', required=False, default=None, type=str, help="The infant's NHI number")
#@click.option('-b', '--birth-date', required=False, default=None, type=click.DateTime(formats=["%Y-%m-%d"]),
#              help="The infant's date of birth")
#@click.option('-d', '--due-date', required=False, default=None, type=click.DateTime(formats=["%Y-%m-%d"]),
#              help="The infant's expected date of birth")
#def update(
#    infant_id: int,
#    full_name: str | None,
#    nhi_number: str | None,
#    birth_date: datetime.datetime | None,
#    due_date: datetime.datetime | None,
#):
#    """Update the specified Infant.
#
#    INFANT_ID is the id of the infant to update.
#    """
#    print(">>>>", birth_date, due_date)
#
#    with Session(database.engine) as session:
#        infant_service = InfantService(session, 0)
#
#        update_obj = InfantUpdate(
#            full_name=full_name,
#            nhi_number=nhi_number,
##            birth_date=birth_date.date() if birth_date is not None else None,
##            due_date=due_date.date() if due_date is not None else None,
#        )
#        if birth_date is not None:
#            update_obj.birth_date = birth_date.date()
#        if due_date is not None:
#            update_obj.due_date = due_date.date()
#        updated_infant = infant_service.update(infant_id, update_obj)
#
#        click.echo(f"Updated infant: {updated_infant!r}")


@infant.command()
@click.argument('infant_id', type=click.INT)
def delete(
    infant_id: int,
):
    """Delete the specified Infant.

    INFANT_ID is the id of the infant to delete.
    """
    with Session(database.engine) as session:
        infant_service = InfantService(session, 0)

        # first get the infant and confirm deletion
        infant_record = infant_service.get(infant_id)
        click.echo(f"Deleting {infant_record!r}")
        delete = click.confirm("Are you sure you want to delete it?")
        if not delete:
            click.echo("Not deleting")
            raise click.Abort()
        else:
            # delete the infant
            infant_service.delete(infant_id)
            print("Deleted infant.")
