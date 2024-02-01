import logging
from typing import Annotated

from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session

from tinymotion_backend import models
from tinymotion_backend.core.config import settings
from tinymotion_backend import database
from tinymotion_backend.services.user_service import UserService


logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")


def get_session():
    with Session(database.engine) as session:
        yield session


def get_token_data(token: str, secret_key: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = models.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
) -> models.User:
    token_data = get_token_data(token, settings.ACCESS_TOKEN_SECRET_KEY)
    user = user_service.get(token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
