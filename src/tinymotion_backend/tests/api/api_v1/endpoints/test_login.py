from fastapi.testclient import TestClient
from sqlmodel import Session

from tinymotion_backend import models


def test_v1_login_access_token(session: Session, client: TestClient):
    # add a user to test against
    test_user = models.User(email="test@example.com", access_key="secretkey")
    session.add(test_user)
    session.commit()

    # call token endpoint
    data = {
        "access_key": "secretkey",
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_v1_login_access_token_wrong(session: Session, client: TestClient):
    # add a user to test against
    test_user = models.User(email="test@example.com", access_key="secretkey")
    session.add(test_user)
    session.commit()

    # call token endpoint
    data = {
        "access_key": "badkey",
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect access key"


def test_v1_login_access_token_disabled(session: Session, client: TestClient):
    # add a user to test against
    test_user = models.User(email="test@example.com", access_key="secretkey", disabled=True)
    session.add(test_user)
    session.commit()

    # call token endpoint
    data = {
        "access_key": "secretkey",
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Login disabled for user"


def test_v1_login_refresh_token(session: Session, client: TestClient):
    # add a user to test against
    test_user = models.User(email="test@example.com", access_key="secretkey")
    session.add(test_user)
    session.commit()

    # call token endpoint
    data = {
        "access_key": "secretkey",
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    refresh_token = data["refresh_token"]

    # call again with refresh token
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_v1_login_refresh_token_user_deleted(session: Session, client: TestClient):
    # add a user to test against
    test_user = models.User(email="test@example.com", access_key="secretkey")
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    # call token endpoint
    data = {
        "access_key": "secretkey",
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    refresh_token = data["refresh_token"]

    # delete user
    session.delete(test_user)
    session.commit()

    # call again with refresh token
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_v1_login_refresh_token_user_disabled(session: Session, client: TestClient):
    # add a user to test against
    test_user = models.User(email="test@example.com", access_key="secretkey")
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    # call token endpoint
    data = {
        "access_key": "secretkey",
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    refresh_token = data["refresh_token"]

    # disable user
    test_user.disabled = True
    session.commit()

    # call again with refresh token
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = client.post("/v1/token", data=data)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Login disabled for user"
