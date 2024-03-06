import os
import datetime
import hashlib

from fastapi.testclient import TestClient
from sqlmodel import Session

from tinymotion_backend import models
from tinymotion_backend.core.config import settings


def test_create_video(
    session: Session,
    client: TestClient,
    access_token_headers: dict[str, str],
    tmp_path,
):
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
    # and a consent
    consent = models.Consent(
        consent_giver_name="Consent Giver",
        consent_giver_email="consent@test.com",
        infant_id=infant.infant_id,
        created_by=1,
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)

    # override video library
    settings.VIDEO_LIBRARY_PATH = str(tmp_path / "videos")
    os.makedirs(settings.VIDEO_LIBRARY_PATH)

    # create a file
    upload_file = tmp_path / "file.mp4"
    upload_file.write_bytes(os.urandom(int(settings.FILE_CHUNK_SIZE_BYTES * 1.6)))
    with upload_file.open('rb') as f:
        fbytes = f.read()
        sha256sum = hashlib.sha256(fbytes).hexdigest()

    # add video
    data_in = {
        "nhi_number": "123xyz",
        "checksum_sha256": sha256sum,
    }
    with upload_file.open('rb') as f:
        response = client.post("/v1/videos", data=data_in, files={'video': f}, headers=access_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["sha256sum"] == sha256sum
    assert data["video_id"] is not None
    assert data["created_by"] == 1
    assert data["created_at"] is not None  # TODO: change this to use freezetime
    assert data["infant_id"] == 1
    assert data["video_name"] is not None
    assert os.path.splitext(data["video_name"])[1] == ".enc"
    assert os.path.exists(os.path.join(settings.VIDEO_LIBRARY_PATH, data["video_name"]))


def test_create_video_wrong_nhi(
    session: Session,
    client: TestClient,
    access_token_headers: dict[str, str],
    tmp_path,
):
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
    # and a consent
    consent = models.Consent(
        consent_giver_name="Consent Giver",
        consent_giver_email="consent@test.com",
        infant_id=infant.infant_id,
        created_by=1,
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)

    # override video library
    settings.VIDEO_LIBRARY_PATH = str(tmp_path / "videos")
    os.makedirs(settings.VIDEO_LIBRARY_PATH)

    # create a file
    upload_file = tmp_path / "file.mp4"
    upload_file.write_bytes(os.urandom(int(settings.FILE_CHUNK_SIZE_BYTES * 1.6)))
    with upload_file.open('rb') as f:
        fbytes = f.read()
        sha256sum = hashlib.sha256(fbytes).hexdigest()

    # add video
    data_in = {
        "nhi_number": "123abc",
        "checksum_sha256": sha256sum,
    }
    with upload_file.open('rb') as f:
        response = client.post("/v1/videos", data=data_in, files={'video': f}, headers=access_token_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "An infant with the specified NHI number does not exist"


def test_create_video_no_consent(
    session: Session,
    client: TestClient,
    access_token_headers: dict[str, str],
    tmp_path,
):
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

    # override video library
    settings.VIDEO_LIBRARY_PATH = str(tmp_path / "videos")
    os.makedirs(settings.VIDEO_LIBRARY_PATH)

    # create a file
    upload_file = tmp_path / "file.mp4"
    upload_file.write_bytes(os.urandom(int(settings.FILE_CHUNK_SIZE_BYTES * 1.6)))
    with upload_file.open('rb') as f:
        fbytes = f.read()
        sha256sum = hashlib.sha256(fbytes).hexdigest()

    # add video
    data_in = {
        "nhi_number": "123xyz",
        "checksum_sha256": sha256sum,
    }
    with upload_file.open('rb') as f:
        response = client.post("/v1/videos", data=data_in, files={'video': f}, headers=access_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "No consent exists"


def test_create_video_not_authenticated(
    session: Session,
    client: TestClient,
    tmp_path,
):
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
    # and a consent
    consent = models.Consent(
        consent_giver_name="Consent Giver",
        consent_giver_email="consent@test.com",
        infant_id=infant.infant_id,
        created_by=1,
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)

    # override video library
    settings.VIDEO_LIBRARY_PATH = str(tmp_path / "videos")
    os.makedirs(settings.VIDEO_LIBRARY_PATH)

    # create a file
    upload_file = tmp_path / "file.mp4"
    upload_file.write_bytes(os.urandom(int(settings.FILE_CHUNK_SIZE_BYTES * 1.6)))
    with upload_file.open('rb') as f:
        fbytes = f.read()
        sha256sum = hashlib.sha256(fbytes).hexdigest()

    # add video
    data_in = {
        "nhi_number": "123abc",
        "checksum_sha256": sha256sum,
    }
    with upload_file.open('rb') as f:
        response = client.post("/v1/videos", data=data_in, files={'video': f})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_create_video_missing_sha256(
    session: Session,
    client: TestClient,
    access_token_headers: dict[str, str],
    tmp_path,
):
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
    # and a consent
    consent = models.Consent(
        consent_giver_name="Consent Giver",
        consent_giver_email="consent@test.com",
        infant_id=infant.infant_id,
        created_by=1,
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)

    # override video library
    settings.VIDEO_LIBRARY_PATH = str(tmp_path / "videos")
    os.makedirs(settings.VIDEO_LIBRARY_PATH)

    # create a file
    upload_file = tmp_path / "file.mp4"
    upload_file.write_bytes(os.urandom(int(settings.FILE_CHUNK_SIZE_BYTES * 1.6)))
    with upload_file.open('rb') as f:
        fbytes = f.read()
        sha256sum = hashlib.sha256(fbytes).hexdigest()

    # add video
    data_in = {
        "nhi_number": "123xyz",
    }
    with upload_file.open('rb') as f:
        response = client.post("/v1/videos", data=data_in, files={'video': f}, headers=access_token_headers)
    assert response.status_code == 422


def test_create_video_checksum_mismatch(
    session: Session,
    client: TestClient,
    access_token_headers: dict[str, str],
    tmp_path,
):
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
    # and a consent
    consent = models.Consent(
        consent_giver_name="Consent Giver",
        consent_giver_email="consent@test.com",
        infant_id=infant.infant_id,
        created_by=1,
    )
    session.add(consent)
    session.commit()
    session.refresh(consent)

    # override video library
    settings.VIDEO_LIBRARY_PATH = str(tmp_path / "videos")
    os.makedirs(settings.VIDEO_LIBRARY_PATH)

    # create a file
    upload_file = tmp_path / "file.mp4"
    upload_file.write_bytes(os.urandom(int(settings.FILE_CHUNK_SIZE_BYTES * 1.6)))
    sha256sum_wrong = "abcd" * 16

    # add video
    data_in = {
        "nhi_number": "123xyz",
        "checksum_sha256": sha256sum_wrong,
    }
    with upload_file.open('rb') as f:
        response = client.post("/v1/videos", data=data_in, files={'video': f}, headers=access_token_headers)
    assert response.status_code == 409
    data = response.json()
    assert data["detail"].startswith("Verification of the SHA256 checksum of the uploaded video failed (")
