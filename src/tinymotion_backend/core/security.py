from datetime import datetime, timedelta

from jose import jwt
#from passlib.context import CryptContext
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm

from tinymotion_backend.core.config import settings


#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class OAuth2PasswordAndRefreshRequestForm(OAuth2PasswordRequestForm):
    """Modified from fastapi.security.OAuth2PasswordRequestForm"""

    def __init__(
        self,
        grant_type: str = Form(default="password", pattern="password|refresh_token"),
        access_key: str = Form(default=""),
        refresh_token: str = Form(default=""),
    ):
        super().__init__(
            grant_type=grant_type,
            username=access_key,
            password="",
            client_id=None,
            client_secret=None,
        )
        self.scopes = []
        self.refresh_token = refresh_token


def create_access_token(
    subject: str, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}

    encoded_jwt = jwt.encode(to_encode, settings.ACCESS_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token(
    subject: str, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}

    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


#def verify_password(plain_password: str, hashed_password: str) -> bool:
#    return pwd_context.verify(plain_password, hashed_password)
#
#
#def get_password_hash(password: str) -> str:
#    return pwd_context.hash(password)
