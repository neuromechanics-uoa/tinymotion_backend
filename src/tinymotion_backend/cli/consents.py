import uuid
import json

import click
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.services.consent_service import ConsentService
from tinymotion_backend.models import ConsentCreate, ConsentUpdate, Consent, Infant
from tinymotion_backend.cli.utils import check_user_id, check_infant_id


@click.group()
def consent():
    """Commands to interact with consents in the backend."""
    pass


@consent.command()
@click.option("-u", "--user-id", required=True, type=click.UUID, help="ID of the User to create the Consent")
@click.option('-i', '--infant-id', required=True, type=click.UUID,
              help="The infant_id of the infant this Consent relates to")
@click.option('-n', '--consent-giver-name', required=False, default=None, type=str, help="The Consent giver's name")
@click.option('-e', '--consent-giver-email', required=False, default=None, type=str, help="The Consent giver's email")
@click.option('-p', '--collected-physically', is_flag=True, default=False,
              help="Flag to indicate if the Consent was collected physically")
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
            click.echo("Error: must specify consent_giver_name and consent_giver_email if not collected_physically")
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
@click.option("-j", "--json-output", is_flag=True, default=False, help="Output JSON only, no extra messages")
def list(pager: bool, json_output: bool):
    """List existing consents."""
    with Session(database.engine) as session:
        # get the list of consents
        consent_service = ConsentService(session, None)
        consents = consent_service.list()
        if not json_output:
            click.echo(f"Found {len(consents)} Consents")

        # build a list of consents in json format
        consents_json = []
        for consent in consents:
            consents_json.append(json.loads(consent.json()))

        # display to screen with pager or not
        if pager and not json_output:
            echo_command = click.echo_via_pager
        else:
            echo_command = click.echo

        echo_command(json.dumps(consents_json, indent=2))


@consent.command()
@click.argument('consent_id', type=click.UUID)
@click.option('-n', '--consent-giver-name', required=False, default=None, type=str,
              help="Update the Consent giver's name")
@click.option('-e', '--consent-giver-email', required=False, default=None, type=str,
              help="Update the Consent giver's email")
@click.option('-p', '--collected-physically', required=False, type=bool, default=None,
              help="Update collected physically flag")
@click.pass_context
def update(
    ctx: click.Context,
    consent_id: uuid.UUID,
    consent_giver_name: str | None,
    consent_giver_email: str | None,
    collected_physically: bool | None,
):
    """Update the specified Consent.

    CONSENT_ID is the id of the consent to update.
    """
    # only update values that were passed, ignore those that are defaults
    update_obj_dict = {}
    if ctx.get_parameter_source("consent_giver_name").name != "DEFAULT":
        update_obj_dict["consent_giver_name"] = consent_giver_name
    if ctx.get_parameter_source("consent_giver_email").name != "DEFAULT":
        update_obj_dict["consent_giver_email"] = consent_giver_email
    if ctx.get_parameter_source("collected_physically").name != "DEFAULT":
        update_obj_dict["collected_physically"] = collected_physically

    # validate passed in values
    update_obj = ConsentUpdate.model_validate(update_obj_dict)

    with Session(database.engine) as session:
        consent_service = ConsentService(session, created_by=None)

        # get the existing consent to validate proposed update
        current_consent = consent_service.get(consent_id)

        # proposed value for consent giver name
        if "consent_giver_name" in update_obj_dict:
            proposed_consent_giver_name = update_obj_dict["consent_giver_name"]
        else:
            proposed_consent_giver_name = current_consent.consent_giver_name

        # proposed value for consent giver email
        if "consent_giver_email" in update_obj_dict:
            proposed_consent_giver_email = update_obj_dict["consent_giver_email"]
        else:
            proposed_consent_giver_email = current_consent.consent_giver_email

        # proposed value for collected_physically
        if "collected_physically" in update_obj_dict:
            proposed_collected_physically = update_obj_dict["collected_physically"]
        else:
            proposed_collected_physically = current_consent.collected_physically

        # validate proposed options
        if (not proposed_collected_physically) and (proposed_consent_giver_name is None
                                                    or proposed_consent_giver_email is None):
            click.echo("Error: proposed combination of parameters is not valid: consent giver name and email "
                       "must be set if consent not collected physically")
            raise click.Abort()

        # now update the stored record
        updated_consent = consent_service.update(consent_id, update_obj)

        click.echo("Updated consent:")
        click.echo(updated_consent.model_dump_json(indent=2))


@consent.command()
@click.argument('consent_id', type=click.UUID)
def delete(
    consent_id: uuid.UUID,
):
    """Delete the specified Consent.

    CONSENT_ID is the id of the Consent to delete.
    """
    with Session(database.engine) as session:
        # first get the consent and determine whether it can be deleted
        consent_service = ConsentService(session, created_by=None)
        consent_record: Consent = consent_service.get(consent_id)
        click.echo("Deleting Consent:")
        click.echo(consent_record.model_dump_json(indent=2))

        # get the infant the consent is for
        infant_service = InfantService(session, created_by=None)
        infant: Infant = infant_service.get(consent_record.infant_id)
        if len(infant.consents) < 2 and len(infant.videos) > 0:
            click.echo("Error: cannot delete only Consent for Infant that has stored Videos")
            raise click.Abort()

        # get confirmation from user
        delete = click.confirm("Are you sure you want to delete it?")
        if not delete:
            click.echo("Not deleting")
            raise click.Abort()
        else:
            # delete the consent
            consent_service.delete(consent_id)
            print("Deleted consent.")
