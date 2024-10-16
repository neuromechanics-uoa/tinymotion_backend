import uuid
import datetime

import pytest
from sqlmodel import Session, select
from click.testing import CliRunner

from tinymotion_backend.cli import cli
from tinymotion_backend.models import Infant, Consent, Video
from tinymotion_backend.tests.mock_data import MOCK_USERS
from tinymotion_backend.core.exc import NotFoundError


@pytest.mark.parametrize("user_id,full_name,nhi_number,birth_date,due_date,exit_code,expected_output", [
    ("1", "An Infant", "abc123", "2024-01-01", "2024-01-02", 0, "Successfully created new infant"),
    ("0", "An Infant", "abc123", "2024-01-01", "2024-01-02", 1, "Error: specified user id is not valid"),
    ("1", "An Infant", "abc123", "20240101", "2024-01-02", 2, "Error: Invalid value for '-b' / '--birth-date'"),
    ("1", "An Infant", None, "2024-01-01", "2024-01-02", 2, "Error: Missing option '-n' / '--nhi-number'"),
])
def test_cli_infant_create(monkeypatch, session: Session, mocked_user_id: uuid.UUID,
                           user_id: str | None, full_name: str | None,
                           nhi_number: str | None, birth_date: str | None, due_date: str | None,
                           exit_code: int, expected_output: str | None):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    if user_id == "1":
        user_id = str(mocked_user_id)
    else:
        user_id = str(uuid.uuid4())

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
        assert infant.created_by == mocked_user_id


@pytest.mark.parametrize("full_name,nhi_number,birth_date,due_date,exit_code,expected_output", [
    ("My Infant", "VBN98765", "2024-12-01", "2024-11-01", 0, "Updated infant"),
    ("NOTSET", "VBN98765", "2024-12-01", "2024-11-01", 0, "Updated infant"),
    ("NOTSET", "NOTSET", "2024-12-01", "2024-11-01", 0, "Updated infant"),
    ("NOTSET", "NOTSET", "NOTSET", "2024-11-01", 0, "Updated infant"),
    ("NOTSET", "ABC5678", "NOTSET", "NOTSET", 0, "Updated infant"),
    ("My Infant", "VBN98765", "20241201", "2024-11-01", 2, "Error: Invalid value for '-b' / '--birth-date'"),
    ("My Infant", "VBN98765", "NOTSET", "20241101", 2, "Error: Invalid value for '-d' / '--due-date'"),
])
def test_cli_infant_update(
    monkeypatch,
    session: Session,
    mocked_user_id: uuid.UUID,
    full_name,
    nhi_number,
    birth_date,
    due_date,
    exit_code,
    expected_output,
):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    # add an infant first
    default_name = "Default Infant"
    default_nhi = "XYZ12345"
    default_birth_date = datetime.date(2023, 1, 3)
    default_due_date = datetime.date(2023, 1, 4)
    infant: Infant = Infant(
        full_name=default_name,
        nhi_number=default_nhi,
        birth_date=default_birth_date,
        due_date=default_due_date,
        created_by=str(mocked_user_id),
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)
    print("Initial Infant:", infant)
    infant_id = infant.infant_id

    # update the infant via cli
    args = ["infant", "update"]
    if full_name != "NOTSET":
        args.extend(["--full-name", full_name])
    if nhi_number != "NOTSET":
        args.extend(["--nhi-number", nhi_number])
    if birth_date != "NOTSET":
        args.extend(["--birth-date", birth_date])
    if due_date != "NOTSET":
        args.extend(["--due-date", due_date])
    args.append(str(infant_id))
    print(args)
    runner = CliRunner()
    result = runner.invoke(cli, args)
    session.commit()
    session.flush()
    print(result)
    print(result.output)
    if expected_output is not None:
        assert expected_output in result.output
    assert result.exit_code == exit_code

    if exit_code == 0:
        infant = session.get(Infant, infant_id)
        print("Infant:", infant)
        assert infant.full_name == full_name if full_name != "NOTSET" else infant.full_name == default_name
        assert infant.nhi_number == nhi_number if nhi_number != "NOTSET" else infant.nhi_number == default_nhi
        if birth_date == "NOTSET":
            assert infant.birth_date == default_birth_date
        else:
            birth_date_dt = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
            assert infant.birth_date == birth_date_dt
        if due_date == "NOTSET":
            assert infant.due_date == default_due_date
        else:
            due_date_dt = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
            assert infant.due_date == due_date_dt


@pytest.mark.parametrize("input_value,exit_code", [
    ("y", 0),
    ("n", 1),
])
def test_cli_infant_delete(monkeypatch, session: Session, mocked_user_id: uuid.UUID, input_value, exit_code):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    # add infant
    infant: Infant = Infant(
        full_name="Infants Name",
        nhi_number="abc12345",
        birth_date=datetime.date(2023, 1, 3),
        due_date=datetime.date(2023, 1, 2),
        created_by=mocked_user_id,
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


@pytest.mark.parametrize("input_value,exit_code", [
    ("y", 0),
    ("n", 1),
])
def test_cli_infant_delete_cascade(monkeypatch, session: Session, mocked_user_id: uuid.UUID, input_value, exit_code):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    # add infant
    infant: Infant = Infant(
        full_name="Infants Name",
        nhi_number="abc12345",
        birth_date=datetime.date(2023, 1, 3),
        due_date=datetime.date(2023, 1, 2),
        created_by=mocked_user_id,
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)
    infant_id = infant.infant_id

    # add consent for this infant
    consent: Consent = Consent(
        infant_id=infant_id,
        created_by=mocked_user_id,
        collected_physically=False,
        consent_giver_email="consent@giver.com",
        consent_giver_name="Consent Giver",
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)
    consent_id = consent.consent_id

    # add video for this infant
    video: Video = Video(
        infant_id=infant_id,
        created_by=mocked_user_id,
        video_name="myvideo",
        sha256sum="abcdefgh"*8,
    )
    session.add(video)
    session.commit()
    session.refresh(video)
    video_id = video.video_id

    # run the cli command
    args = ["infant", "delete", str(infant_id)]
    runner = CliRunner()
    result = runner.invoke(cli, args, input=input_value)

    if input_value == "y":
        assert "Deleted infant" in result.output
        assert result.exit_code == exit_code
        session.expunge_all()

        # check the infant was deleted
        infant = session.get(Infant, infant_id)
        assert infant is None

        # check the consent was deleted
        consent = session.get(Consent, consent_id)
        assert consent is None

        # check the video was deleted
        video = session.get(Video, video_id)
        assert video is None

    else:
        assert "Not deleting" in result.output
        assert result.exit_code == exit_code
        infant = session.get(Infant, infant_id)
        assert infant is not None
        consent = session.get(Consent, consent_id)
        assert consent is not None
        video = session.get(Video, video_id)
        assert video is not None


@pytest.mark.parametrize("num_add", [
    0,
    1,
    4,
])
def test_cli_infant_list(monkeypatch, session: Session, mocked_user_id: uuid.UUID, num_add: int):
    engine = session.get_bind()
    monkeypatch.setattr('tinymotion_backend.database.engine', engine)

    for i in range(num_add):
        infant: Infant = Infant(
            full_name="An Infant",
            nhi_number=f"abc{i}",
            birth_date=datetime.date(2024, 3, i + 1),
            due_date=datetime.date(2024, 2, i + 2),
            created_by=mocked_user_id,
        )
        session.add(infant)
        session.commit()

    runner = CliRunner()
    result = runner.invoke(cli, ["infant", "list"])

    assert result.exit_code == 0
    assert f"Found {num_add} Infants" in result.output
