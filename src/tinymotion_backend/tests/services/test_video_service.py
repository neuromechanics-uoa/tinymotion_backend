import datetime
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from freezegun import freeze_time

from tinymotion_backend.services.video_service import VideoService
from tinymotion_backend.models import VideoCreateViaNHI, Infant, Consent
from tinymotion_backend.core.exc import NotFoundError, NoConsentError


def test_video_service_create_video_nhi(session: Session, client: TestClient, mocked_user_id: uuid.UUID):
    # create an infant that we can add the video to
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
    # and a consent
    consent = Consent(
        consent_giver_name="Consent Giver",
        consent_giver_email="consent@test.com",
        infant_id=infant.infant_id,
        created_by=mocked_user_id,
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)

    # add the video
    video_service = VideoService(session, created_by=mocked_user_id)
    video_in = VideoCreateViaNHI(
        video_name="myvideo.mp4",
        sha256sum="qwertyuiopasdfghjklzxcvbnm123456qwertyuiopasdfghjklzxcvbnm123456",
        nhi_number="abcdefg",
    )
    with freeze_time("2024-03-01 16:31:23"):
        video = video_service.create_using_nhi_number(video_in)
    assert video.video_name == "myvideo.mp4"
    assert video.sha256sum == "qwertyuiopasdfghjklzxcvbnm123456qwertyuiopasdfghjklzxcvbnm123456"
    assert video.infant_id == infant.infant_id
    assert video.created_by == mocked_user_id
#    assert video.created_at == "2024-03-01 16:31:23"
    assert video.video_id is not None


def test_video_service_create_video_invalid_nhi(session: Session, client: TestClient, mocked_user_id: uuid.UUID):
    # create an infant that we can add the video to
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
    # and a consent
    consent = Consent(
        consent_giver_name="Consent Giver",
        consent_giver_email="consent@test.com",
        infant_id=infant.infant_id,
        created_by=mocked_user_id,
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)

    # add the video
    video_service = VideoService(session, created_by=mocked_user_id)
    video_in = VideoCreateViaNHI(
        video_name="myvideo.mp4",
        sha256sum="qwertyuiopasdfghjklzxcvbnm123456qwertyuiopasdfghjklzxcvbnm123456",
        nhi_number="abcdefh",
    )

    with pytest.raises(NotFoundError):
        video_service.create_using_nhi_number(video_in)


def test_video_service_create_video_no_consent(session: Session, client: TestClient, mocked_user_id: uuid.UUID):
    # create an infant that we can add the video to
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

    # add the video
    video_service = VideoService(session, created_by=mocked_user_id)
    video_in = VideoCreateViaNHI(
        video_name="myvideo.mp4",
        sha256sum="qwertyuiopasdfghjklzxcvbnm123456qwertyuiopasdfghjklzxcvbnm123456",
        nhi_number="abcdefg",
    )

    with pytest.raises(NoConsentError):
        video_service.create_using_nhi_number(video_in)
