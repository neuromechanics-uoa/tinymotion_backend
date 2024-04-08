import datetime
import pytest
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session
from freezegun import freeze_time

from tinymotion_backend.services.consent_service import ConsentService
from tinymotion_backend.models import ConsentCreateViaNHI, Infant
from tinymotion_backend.core.exc import NotFoundError


def test_consent_service_create_consent_nhi(session: Session, client: TestClient, mocked_user_id: uuid.UUID):
    # create an infant that we can add the consent to
    infant = Infant(
        full_name="An Infant",
        birth_date=datetime.date(2023, 6, 1),
        due_date=datetime.date(2023, 7, 1),
        nhi_number="abcdefg",
        created_by=mocked_user_id,
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add the consent
    consent_service = ConsentService(session, created_by=mocked_user_id)
    consent_in = ConsentCreateViaNHI(
        consent_giver_email="consent@giver.com",
        consent_giver_name="Consent Giver",
        collected_physically=False,
        nhi_number="abcdefg",
    )
    with freeze_time("2024-03-01 16:31:23"):
        consent = consent_service.create_using_nhi_number(consent_in)
    assert consent.consent_giver_name == "Consent Giver"
    assert consent.consent_giver_email == "consent@giver.com"
    assert not consent.collected_physically
    assert consent.infant_id == infant.infant_id
    assert consent.created_by == mocked_user_id
#    assert consent.created_at == "2024-03-01 16:31:23"
    assert consent.consent_id is not None


def test_consent_service_create_consent_invalid_nhi(session: Session, client: TestClient, mocked_user_id: uuid.UUID):
    # create an infant that we can add the consent to
    infant = Infant(
        full_name="An Infant",
        birth_date=datetime.date(2023, 6, 1),
        due_date=datetime.date(2023, 7, 1),
        nhi_number="abcdefg",
        created_by=mocked_user_id,
    )
    session.add(infant)
    session.commit()
    session.refresh(infant)

    # add the consent
    consent_service = ConsentService(session, created_by=mocked_user_id)
    consent_in = ConsentCreateViaNHI(
        consent_giver_email="consent@giver.com",
        consent_giver_name="Consent Giver",
        collected_physically=False,
        nhi_number="uvwxyz",
    )
    with pytest.raises(NotFoundError):
        consent_service.create_using_nhi_number(consent_in)
