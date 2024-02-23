from datetime import timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException

from tinymotion_backend.api import deps
from tinymotion_backend.core import security
from tinymotion_backend.core.config import settings
from tinymotion_backend import models
from tinymotion_backend.services.user_service import UserService


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=models.Token,
    responses={
        400: {
            "description": "Bad Request",
            "content": {"application/json": {"example": {"detail": "Login disabled for user"}}},
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Incorrect access key"}}},
        },
        404: {
            "description": "Not Found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        },
    },
)
def login_for_tokens(
    form_data: security.OAuth2PasswordAndRefreshRequestForm = Depends(),
    user_service: UserService = Depends(deps.get_user_service)
):
    """
    Login to get access and refresh tokens to use with future requests:

    - if `grant_type` is "password" then the access key must be passed in the `username` field,
      all other fields can be blank
    - if `grant_type` is "refresh_token" then `refresh_token` must be present, all other fields
      can be blank

    """
    if form_data.grant_type == "refresh_token":
        logger.debug("Running login grant_type=refresh_token ...")
        token_data = deps.get_token_data(
            token=form_data.refresh_token,
            secret_key=settings.REFRESH_TOKEN_SECRET_KEY,
        )
        user = user_service.get(token_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    else:
        logger.debug("Running login grant_type=password ...")
        # the username in the form is the access key
        user = user_service.authenticate(form_data.username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect access key",
                headers={"WWW-Authenticate": "Bearer"}
            )

    if user.disabled:
        raise HTTPException(status_code=400, detail="Login disabled for user", headers={"WWW-Authenticate": "Bearer"})

    # create the access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.user_id, expires_delta=access_token_expires
    )

    # create the refresh token
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        user.user_id, expires_delta=refresh_token_expires
    )

    return models.Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=access_token_expires.seconds,
    )
