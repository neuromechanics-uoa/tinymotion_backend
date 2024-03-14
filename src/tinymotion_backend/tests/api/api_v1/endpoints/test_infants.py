import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from tinymotion_backend import models


def test_create_infant(client: TestClient, access_token_headers: dict[str, str]):
    infant_data = {
        "full_name": "An Infant",
        "birth_date": "2024-02-01",
        "due_date": "2024-01-01",
        "nhi_number": "123xyz",
    }
    response = client.post("/v1/infants", json=infant_data, headers=access_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "An Infant"
    assert data["birth_date"] == "2024-02-01"
    assert data["due_date"] == "2024-01-01"
    assert data["nhi_number"] == "123xyz"
    assert data["infant_id"] is not None


def test_create_infant_duplicate(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    infant_add = models.Infant(
        full_name="Another infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 2, 1),
        nhi_number="123xyz",
        created_by=1,
    )
    session.add(infant_add)
    session.commit()

    infant_data = {
        "full_name": "An Infant",
        "birth_date": "2024-02-01",
        "due_date": "2024-01-01",
        "nhi_number": "123xyz",
    }
    response = client.post("/v1/infants", json=infant_data, headers=access_token_headers)
    assert response.status_code == 409


def test_create_infant_not_authenticated(client: TestClient):
    infant_data = {
        "full_name": "An Infant",
        "birth_date": "2024-02-01",
        "due_date": "2024-01-01",
        "nhi_number": "123xyz",
    }
    response = client.post("/v1/infants", json=infant_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
