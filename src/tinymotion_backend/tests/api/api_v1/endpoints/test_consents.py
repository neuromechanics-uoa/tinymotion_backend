import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from tinymotion_backend import models


def test_create_consent(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "consent_giver_name": "Consent Giver",
        "consent_giver_email": "consent@giver.com",
        "collected_physically": False,
        "nhi_number": "123xyz",
    }
    response = client.post("/v1/consents", json=consent_in, headers=access_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["consent_giver_name"] == "Consent Giver"
    assert data["consent_giver_email"] == "consent@giver.com"
    assert not data["collected_physically"]
    assert data["consent_id"] is not None
    assert data["created_by"] == 1
    assert data["created_at"] is not None  # TODO: change this to use freezetime
    assert data["infant_id"] == 1


def test_create_consent_2(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    # add another infant
    infant = models.Infant(
        full_name="Another Infant",
        birth_date=datetime.date(2023, 2, 1),
        due_date=datetime.date(2023, 1, 1),
        nhi_number="abcdefg",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "consent_giver_name": "Consent Giver",
        "consent_giver_email": "consent@giver.com",
        "nhi_number": "abcdefg",
    }
    response = client.post("/v1/consents", json=consent_in, headers=access_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["consent_giver_name"] == "Consent Giver"
    assert data["consent_giver_email"] == "consent@giver.com"
    assert not data["collected_physically"]
    assert data["consent_id"] is not None
    assert data["created_by"] == 1
    assert data["created_at"] is not None  # TODO: change this to use freezetime
    assert data["infant_id"] == 2


def test_create_consent_wrong_nhi(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "consent_giver_name": "Consent Giver",
        "consent_giver_email": "consent@giver.com",
        "collected_physically": False,
        "nhi_number": "123abc",
    }
    response = client.post("/v1/consents", json=consent_in, headers=access_token_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "An infant with the specified NHI number does not exist"


def test_create_consent_not_authenticated(session: Session, client: TestClient):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "consent_giver_name": "Consent Giver",
        "consent_giver_email": "consent@giver.com",
        "collected_physically": False,
        "nhi_number": "123xyz",
    }
    response = client.post("/v1/consents", json=consent_in)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_consent_physically(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "collected_physically": True,
        "nhi_number": "123xyz",
    }
    response = client.post("/v1/consents", json=consent_in, headers=access_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["consent_giver_name"] is None
    assert data["consent_giver_email"] is None
    assert data["collected_physically"]
    assert data["consent_id"] is not None
    assert data["created_by"] == 1
    assert data["created_at"] is not None  # TODO: change this to use freezetime
    assert data["infant_id"] == 1


def test_create_consent_missing_nhi(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "collected_physically": True,
    }
    response = client.post("/v1/consents", json=consent_in, headers=access_token_headers)
    assert response.status_code == 422
    # TODO: check nhi missing in detail...


def test_create_consent_missing_email(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "nhi_number": "123xyz",
    }
    response = client.post("/v1/consents", json=consent_in, headers=access_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Must set `consent_giver_email` when not specifying `collected_physically`"


def test_create_consent_missing_name(session: Session, client: TestClient, access_token_headers: dict[str, str]):
    # add an infant first
    infant = models.Infant(
        full_name="An Infant",
        birth_date=datetime.date(2024, 2, 1),
        due_date=datetime.date(2024, 1, 1),
        nhi_number="123xyz",
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add consent
    consent_in = {
        "nhi_number": "123xyz",
        "consent_giver_email": "email@consent.com",
    }
    response = client.post("/v1/consents", json=consent_in, headers=access_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Must set `consent_giver_name` when not specifying `collected_physically`"
