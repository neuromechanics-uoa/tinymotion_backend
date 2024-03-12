import pytest
from sqlmodel import Session, select
from click.testing import CliRunner

from tinymotion_backend.cli import cli
from tinymotion_backend.models import User
from tinymotion_backend.tests.mock_data import MOCK_USERS
from tinymotion_backend.core.exc import NotFoundError


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


@pytest.mark.parametrize("email,key,disabled,exit_code", [
    ("cli@test.com", "clisecretkey", None, 0),
    ("cli@test.com", "clisecretkey", True, 0),
    (None, "clisecretkey", False, 0),
    ("cli@test.com", None, None, 0),
    ("notanemail", "clisecretkey", True, 1),
])
def test_cli_user_update(monkeypatch, session: Session, email, key, disabled, exit_code):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    user_id = "1"  # the user added via mock data
    args = ["users", "update"]
    if email is not None:
        args.extend(["--email", email])
    if key is not None:
        args.extend(["-k", key])
    if disabled is not None:
        args.extend(["--disabled", "1" if disabled else "0"])
    args.append(user_id)
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code == exit_code

    if exit_code == 0:
        user = session.get(User, user_id)
        assert user.email == email if email is not None else user.email == MOCK_USERS[0]["email"]
        assert user.access_key == key if key is not None else user.access_key == MOCK_USERS[0]["access_key"]
        if disabled is not None:
            assert user.disabled is disabled
        else:
            assert user.disabled is MOCK_USERS[0]["disabled"]


@pytest.mark.parametrize("input_value,exit_code", [
    pytest.param("y", 0, marks=pytest.mark.xfail(reason="Still able to get User")),
    ("n", 1),
])
def test_cli_user_delete(monkeypatch, session: Session, input_value, exit_code):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    user_id = "1"  # the user added via mock data

    # check the user exists first
    user = session.get(User, user_id)

    args = ["users", "delete", user_id]
    runner = CliRunner()
    result = runner.invoke(cli, args, input=input_value)

    if input_value == "y":
        assert result.exit_code == exit_code
        with pytest.raises(NotFoundError):
            session.get(User, user_id)
    else:
        assert result.exit_code == exit_code
        session.get(User, user_id)


@pytest.mark.parametrize("num_add", [
    0,
    1,
    4,
])
def test_cli_user_list(monkeypatch, session: Session, num_add):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    for i in range(num_add):
        user = User(
            email=f"an{i}@email.com",
            access_key=f"mysecretkey{i}",
            disabled=False,
        )
        session.add(user)
        session.commit()

    runner = CliRunner()
    result = runner.invoke(cli, ["users", "list"])

    assert result.exit_code == 0
    assert f"Found {num_add + 1} users" in result.output
