import typer
from typing import Annotated
from sqlmodel import Session

from tinymotion_backend import database
from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.models import UserCreate


app = typer.Typer()


@app.command()
def create_user(
    email: Annotated[str, typer.Argument(help="The new user's email", default=None)],
    access_key: Annotated[str, typer.Argument(help="The new user's access key that they will use to login", default=None)],
    disabled: Annotated[bool, typer.Option(help="Whether the account should be disabled on creation", default=False)] = False,
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

    print(f"Successfully added new user: {user_added!r}")


@app.command()
def list_users():
    """
    List existing users.

    """
    with Session(database.engine) as session:
        user_service = UserService(session)
        users = user_service.list()
        print(f"Found {len(users)} users")
        for user in users:
            print(repr(user))
