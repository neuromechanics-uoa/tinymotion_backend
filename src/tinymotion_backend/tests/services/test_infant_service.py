import datetime
import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session
from pydantic import ValidationError

from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.models import InfantCreate


def test_user_service_create_user(session: Session, client: TestClient):
    infant_service = InfantService(session)
    infant_in = InfantCreate(full_name="An Infant", birth_date="2024-01-01", due_date="2024-01-02", nhi_number="123456")
    infant_added = infant_service.create(infant_in)
    assert infant_added.full_name == "An Infant"
    assert infant_added.birth_date == datetime.date(2024, 1, 1)
    assert infant_added.due_date == datetime.date(2024, 1, 2)
    assert infant_added.nhi_number == "123456"
    assert infant_added.infant_id is not None


def test_user_service_create_user_missing_data(session: Session, client: TestClient):
    infant_service = InfantService(session)
    with pytest.raises(ValidationError):
        infant_in = InfantCreate(full_name="An Infant", birth_date="2024-01-01", due_date="2024-01-02")
