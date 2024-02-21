from fastapi.testclient import TestClient
from sqlmodel import Session
import pytest

from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.models import UserCreate
from tinymotion_backend.tests import mock_data
from tinymotion_backend.core.exc import UniqueConstraintError


def test_user_service_create_user(session: Session):
    user_service = UserService(session)
    user_in = UserCreate(email="test@example.com", access_key="myverysecretkey")
    user_added = user_service.create(user_in)
    assert user_added.email == "test@example.com"
    assert user_added.access_key == "myverysecretkey"
    assert not user_added.disabled
    assert user_added.user_id is not None


def test_user_service_create_user_duplicate_access_key(session: Session):
    user_service = UserService(session)
    user_in = UserCreate(email="new@test.com", access_key=mock_data.MOCK_USERS[0]["access_key"])
    with pytest.raises(UniqueConstraintError):
        user_service.create(user_in)
