import pytest
import datetime
from sqlmodel import Session, select
from click.testing import CliRunner

from tinymotion_backend.cli import cli
from tinymotion_backend.models import Infant
from tinymotion_backend.tests.mock_data import MOCK_USERS
from tinymotion_backend.core.exc import NotFoundError


@pytest.mark.parametrize("user_id,full_name,nhi_number,birth_date,due_date,exit_code,expected_output", [
    ("1", "An Infant", "abc123", "2024-01-01", "2024-01-02", 0, "Successfully added new infant"),
    ("0", "An Infant", "abc123", "2024-01-01", "2024-01-02", 1, "Error: specified user id is not valid"),
    ("1", "An Infant", "abc123", "20240101", "2024-01-02", 2, "Error: Invalid value for '-b' / '--birth-date'"),
    ("1", "An Infant", None, "2024-01-01", "2024-01-02", 2, "Error: Missing option '-n' / '--nhi-number'"),
])
def test_cli_infant_create(monkeypatch, session: Session, user_id: str | None, full_name: str | None,
                           nhi_number: str | None, birth_date: str | None, due_date: str | None,
                           exit_code: int, expected_output: str | None):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    args = ["infant", "create"]
    if user_id is not None:
        args.extend(["-u", user_id])
    if full_name is not None:
        args.extend(["--full-name", full_name])
    if nhi_number is not None:
        args.extend(["-n", nhi_number])
    if birth_date is not None:
        args.extend(["--birth-date", birth_date])
    if due_date is not None:
        args.extend(["--due-date", due_date])
    runner = CliRunner()
    result = runner.invoke(cli, args)
    if expected_output is not None:
        assert expected_output in result.output
    assert result.exit_code == exit_code

    if exit_code == 0:
        infant: Infant = session.exec(
            select(Infant).where(Infant.nhi_number == nhi_number)
        ).one()
        assert infant.full_name == full_name
        assert infant.birth_date == datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
        assert infant.due_date == datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
        assert infant.created_by == int(user_id)


#@pytest.mark.parametrize("full_name,nhi_number,birth_date,due_date,exit_code,expected_output", [
#    ("An Infant", "abc123", "2024-01-01", "2024-01-02", 0, "Updated infant"),
#    (None, "abcd12345", "2024-01-01", "2024-01-02", 0, "Updated infant"),
#    ("An Infant", None, "2024-01-01", "2024-01-02", 0, "Updated infant"),
#    ("An Infant", "abc123", None, "2024-01-02", 0, "Updated infant"),
#    ("An Infant", "abc123", "2024-01-01", None, 0, "Updated infant"),
#    (None, None, None, "2024-01-02", 0, "Updated infant"),
#    ("An Infant", "abc123", "20240101", "2024-01-02", 2, "Error: Invalid value for '-b' / '--birth-date'"),
#])
#def test_cli_infant_update(monkeypatch, session: Session, full_name: str | None,
#                           nhi_number: str | None, birth_date: str | None, due_date: str | None,
#                           exit_code: int, expected_output: str | None):
#    engine = session.get_bind()
#    monkeypatch.setattr('tinymotion_backend.database.engine', engine)
#
#    # add infant
#    default_name = "Default Name"
#    default_nhi = "default1234"
#    default_birth_date = datetime.date(2023, 1, 3)
#    default_due_date = datetime.date(2023, 1, 2)
#    infant: Infant = Infant(
#        full_name=default_name,
#        nhi_number=default_nhi,
#        birth_date=default_birth_date,
#        due_date=default_due_date,
#        created_by=1,
#    )
#    session.add(infant)
#    session.commit()
#    session.refresh(infant)
#    infant_id = infant.infant_id
#
#    # call cli to update infant
#    args = ["infant", "update", str(infant_id)]
#    if full_name is not None:
#        args.extend(["--full-name", full_name])
#    if nhi_number is not None:
#        args.extend(["-n", nhi_number])
#    if birth_date is not None:
#        args.extend(["--birth-date", birth_date])
#    if due_date is not None:
#        args.extend(["--due-date", due_date])
#    runner = CliRunner()
#    print(args)
#    result = runner.invoke(cli, args)
#    if expected_output is not None:
#        assert expected_output in result.output
#    assert result.exit_code == exit_code
#
#    if exit_code == 0:
#        infant: Infant = session.get(Infant, infant_id)
#        assert infant.full_name == full_name if full_name is not None else infant.full_name == default_name
#        assert infant.nhi_number == nhi_number if nhi_number is not None else infant.nhi_number == default_nhi


@pytest.mark.parametrize("input_value,exit_code", [
    ("y", 0),
    ("n", 1),
])
def test_cli_infant_delete(monkeypatch, session: Session, input_value, exit_code):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    # add infant
    infant: Infant = Infant(
        full_name="Infants Name",
        nhi_number="abc12345",
        birth_date=datetime.date(2023, 1, 3),
        due_date=datetime.date(2023, 1, 2),
        created_by=1,
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)
    infant_id = infant.infant_id

    # run the cli command
    args = ["infant", "delete", str(infant_id)]
    runner = CliRunner()
    result = runner.invoke(cli, args, input=input_value)

    if input_value == "y":
        assert "Deleted infant" in result.output
        assert result.exit_code == exit_code
        session.expunge_all()
        infant = session.get(Infant, infant_id)
        assert infant is None
    else:
        assert "Not deleting" in result.output
        assert result.exit_code == exit_code
        infant = session.get(Infant, infant_id)
        assert infant is not None


@pytest.mark.parametrize("num_add", [
    0,
    1,
    4,
])
def test_cli_infant_list(monkeypatch, session: Session, num_add: int):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    for i in range(num_add):
        infant: Infant = Infant(
            full_name="An Infant",
            nhi_number=f"abc{i}",
            birth_date=datetime.date(2024, 3, i + 1),
            due_date=datetime.date(2024, 2, i + 2),
            created_by=1,
        )
        session.add(infant)
        session.commit()

    runner = CliRunner()
    result = runner.invoke(cli, ["infant", "list"])

    assert result.exit_code == 0
    assert f"Found {num_add} infants" in result.output
