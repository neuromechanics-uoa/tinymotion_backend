from fastapi.testclient import TestClient
from sqlmodel import Session

from tinymotion_backend.services.user_service import UserService
from tinymotion_backend.models import UserCreate


def test_user_service_create_user(session: Session, client: TestClient):
    user_service = UserService(session)
    user_in = UserCreate(email="test@example.com", access_key="mysecretkey")
    user_added = user_service.create(user_in)
    assert user_added.email == "test@example.com"
    assert user_added.access_key == "mysecretkey"
    assert not user_added.disabled
    assert user_added.user_id is not None
