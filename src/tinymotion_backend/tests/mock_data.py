import uuid

from sqlmodel import Session

from tinymotion_backend import models


MOCK_USERS = [
    {
        "email": "test@test.com",
        "access_key": "mysecretkey",
        "disabled": False,
    },
]


def insert_mocked_data(session: Session):
    for user_in in MOCK_USERS:
        user_in["user_id"] = uuid.uuid4()
        user_to_add = models.User.model_validate(user_in)
        session.add(user_to_add)
    session.commit()
