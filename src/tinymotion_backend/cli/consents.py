import uuid
import json

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.consent_service import ConsentService
from tinymotion_backend.models import ConsentCreate, ConsentUpdate
from tinymotion_backend.cli.utils import check_user_id, check_infant_id


@click.group()
def consent():
    """Commands to interact with consents in the backend."""
    pass


@consent.command()
@click.option("-u", "--user-id", required=True, type=click.UUID, help="ID of the User to create the Consent")
@click.option('-i', '--infant-id', required=True, type=click.UUID, help="The infant_id of the infant this Consent relates to")
@click.option('-n', '--consent-giver-name', required=False, default=None, type=str, help="The Consent giver's name")
@click.option('-e', '--consent-giver-email', required=False, default=None, type=str, help="The Consent giver's email")
@click.option('-p', '--collected-physically', is_flag=True, default=False, help="Flag to indicate if the Consent was collected physically")
def create(
    user_id: uuid.UUID,
    infant_id: uuid.UUID,
    consent_giver_name: str,
    consent_giver_email: str,
    collected_physically: bool,
):
    """Create a new consent."""
    # check for valid user id
    check_user_id(user_id)

    # check for valid infant id
    check_infant_id(infant_id)

    # check valid combination of options
    if not collected_physically:
        if not (consent_giver_name and consent_giver_email):
            click.echo(f"Error: must specify consent_giver_name and consent_giver_email if not collected_physically")
            raise click.Abort()

    # add the new consent
    new_consent = ConsentCreate(
        infant_id=infant_id,
        consent_giver_name=consent_giver_name,
        consent_giver_email=consent_giver_email,
        collected_physically=collected_physically,
    )

    with Session(database.engine) as session:
        consent_service = ConsentService(session, user_id)
        consent_added = consent_service.create(new_consent)

    click.echo("Successfully created new consent:")
    click.echo(json.dumps(json.loads(consent_added.json()), indent=2))


@consent.command()
@click.option("-p", "--pager", is_flag=True, default=False, help="Display results using a pager")
def list(pager: bool):
    """List existing consents."""
    with Session(database.engine) as session:
        consent_service = ConsentService(session, None)
        consents = consent_service.list()
        click.echo(f"Found {len(consents)} consents:")
        consents_json = []
        for consent in consents:
            consents_json.append(json.loads(consent.json()))
        if pager:
            echo_command = click.echo_via_pager
        else:
            echo_command = click.echo
        echo_command(json.dumps(consents_json, indent=2))


#@user.command()
#@click.argument('user_id', type=click.UUID)
#@click.option('-e', '--email', required=False, default=None, type=str, help="Update the user's email")
#@click.option('-k', '--access-key', required=False, default=None, type=str, help="Update the user's access key")
#@click.option('-d', '--disabled', required=False, default=None, type=bool, help="Update whether the user is disabled")
#def update(
#    user_id: uuid.UUID,
#    email: str | None,
#    access_key: str | None,
#    disabled: bool | None,
#):
#    """Update the specified User.
#
#    USER_ID is the id of the user to update.
#    """
#    with Session(database.engine) as session:
#        user_service = UserService(session)
#
#        update_obj = UserUpdate(
#            email=email,
#            access_key=access_key,
#            disabled=disabled,
#        )
#        updated_user = user_service.update(user_id, update_obj)
#
#        click.echo("Updated user:")
#        click.echo(json.dumps(json.loads(updated_user.json()), indent=2))
#
#
#@user.command()
#@click.argument('user_id', type=click.UUID)
#def delete(
#    user_id: uuid.UUID,
#):
#    """Delete the specified User.
#
#    USER_ID is the id of the user to delete.
#    """
#    with Session(database.engine) as session:
#        user_service = UserService(session)
#
#        # first get the user and confirm deletion
#        user_record = user_service.get(user_id)
#        click.echo("Deleting user:")
#        click.echo(json.dumps(json.loads(user_record.json()), indent=2))
#        delete = click.confirm("Are you sure you want to delete it?")
#        if not delete:
#            click.echo("Not deleting")
#            raise click.Abort()
#        else:
#            # delete the user
#            user_service.delete(user_id)
#            print("Deleted user.")
