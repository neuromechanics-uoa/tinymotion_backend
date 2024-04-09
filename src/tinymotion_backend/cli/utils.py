import uuid

import click
from sqlmodel import Session

from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend import database
from tinymotion_backend.core.exc import NotFoundError


def check_user_id(user_id: uuid.UUID):
    """Check that the passed user ID is valid"""
    with Session(database.engine) as session:
        user_service = UserService(session)

        try:
            user_service.get(user_id)
        except NotFoundError:
            click.echo(f"Error: specified user id is not valid ({user_id})!")
            raise click.Abort()


def check_infant_id(infant_id: uuid.UUID):
    """Check that the passed infant ID is valid"""
    with Session(database.engine) as session:
        infant_service = InfantService(session, None)

        try:
            infant_service.get(infant_id)
        except NotFoundError:
            click.echo(f"Error: specified infant id is not valid ({infant_id})!")
            raise click.Abort()
