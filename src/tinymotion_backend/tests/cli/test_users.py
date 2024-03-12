import pytest
from sqlmodel import Session, select
from click.testing import CliRunner

from tinymotion_backend.cli import cli
from tinymotion_backend.models import User


@pytest.mark.parametrize("email,key,disabled,exit_code", [
    ("cli@test.com", "clisecretkey", None, 0),
    ("cli@test.com", "clisecretkey", True, 0),
    (None, "clisecretkey", None, 2),
    ("cli@test.com", None, None, 2),
    ("notanemail", "clisecretkey", True, 1),
])
def test_cli_user_create(monkeypatch, session: Session, email, key, disabled, exit_code):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    args = ["users", "create"]
    if email is not None:
        args.extend(["--email", email])
    if key is not None:
        args.extend(["-k", key])
    if disabled is not None:
        if disabled:
            args.extend(["--disabled"])
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code == exit_code

    if exit_code == 0:
        user = session.exec(
            select(User).where(User.access_key == key)
        ).one()
        assert user.email == email
        assert user.disabled is False if not disabled else True
