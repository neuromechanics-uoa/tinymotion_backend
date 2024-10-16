import datetime
import pytest
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session
from pydantic import ValidationError
import sqlalchemy

from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.models import InfantCreate


def test_infant_service_create_user(session: Session, client: TestClient, mocked_user_id: uuid.UUID):
    infant_service = InfantService(session, mocked_user_id)
    infant_in = InfantCreate(full_name="An Infant", birth_date="2024-01-01", due_date="2024-01-02", nhi_number="123456")
    infant_added = infant_service.create(infant_in)
    assert infant_added.full_name == "An Infant"
    assert infant_added.birth_date == datetime.date(2024, 1, 1)
    assert infant_added.due_date == datetime.date(2024, 1, 2)
    assert infant_added.nhi_number == "123456"
    assert infant_added.infant_id is not None
    assert infant_added.created_by == mocked_user_id


def test_infant_service_create_user_missing_data(session: Session, client: TestClient):
    with pytest.raises(ValidationError):
        InfantCreate(full_name="An Infant", birth_date="2024-01-01", due_date="2024-01-02")


def test_infant_service_create_user_foreign_key_constraint_failed(
    session: Session,
    client: TestClient,
    mocked_user_id: uuid.UUID,
):
    infant_service = InfantService(session, uuid.uuid4())
    infant_in = InfantCreate(full_name="An Infant", birth_date="2024-01-01", due_date="2024-01-02", nhi_number="123456")
    with pytest.raises(sqlalchemy.exc.IntegrityError) as exc_info:
        infant_service.create(infant_in)
    assert "FOREIGN KEY constraint failed" in str(exc_info.value)
