import os
import uuid
from unittest import mock
import secrets

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from cryptography.fernet import Fernet

from tinymotion_backend.main import app
from tinymotion_backend.api.deps import get_session
from tinymotion_backend import models  # noqa
from tinymotion_backend.tests import mock_data


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(os.environ, {"ACCESS_TOKEN_SECRET_KEY": secrets.token_urlsafe(32),
                                      "REFRESH_TOKEN_SECRET_KEY": secrets.token_urlsafe(32),
                                      "VIDEO_SECRET_KEY": secrets.token_urlsafe(32),
                                      "DATABASE_SECRET_KEY": Fernet.generate_key().decode('ascii')}):
        yield


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        mock_data.insert_mocked_data(session)
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def access_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": mock_data.MOCK_USERS[0]["access_key"],
    }
    r = client.post("/v1/token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    return headers


@pytest.fixture(scope="function")
def mocked_user_id(session: Session) -> uuid.UUID:
    mocked_user_access_key: str = mock_data.MOCK_USERS[0]["access_key"]
    user: models.User = session.exec(
        select(models.User).where(models.User.access_key == mocked_user_access_key)
    ).one()

    return user.user_id
