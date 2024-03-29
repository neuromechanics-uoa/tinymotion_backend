import click
from sqlmodel import Session

from tinymotion_backend.services.user_service import UserService
from tinymotion_backend import database
from tinymotion_backend.core.exc import NotFoundError


def check_user_id(user_id: int):
    """Check that the passed user ID is valid"""
    with Session(database.engine) as session:
        user_service = UserService(session)

        try:
            user_service.get(user_id)
        except NotFoundError:
            click.echo(f"Error: specified user id is not valid ({user_id})!")
            raise click.Abort()
