import logging

from fastapi import APIRouter, Depends, HTTPException

from tinymotion_backend.api import deps
from tinymotion_backend import models
from tinymotion_backend.services.infant_service import InfantService
from tinymotion_backend.core.exc import UniqueConstraintError


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=models.InfantOut,
    responses={
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Not authenticated"}}},
        },
        409: {
            "description": "Conflict Error",
            "content": {"application/json": {"example": {"detail": "Failed to create infant due to unique constraint"}}},
        },
    },
)
def create_infant(
    infant_in: models.InfantCreate,
    infant_service: InfantService = Depends(deps.get_infant_service),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Create an infant

    """
    logger.debug(f"Creating infant: {infant_in!r}")
    logger.debug(f"Current user: {current_user!r}")

    try:
        new_infant = infant_service.create(infant_in)
    except UniqueConstraintError as exc:
        logger.error(f"Error creating infant: {exc}")
        raise HTTPException(
            status_code=409,
            detail="Failed to create infant due to unique constraint",
        )

    logger.debug(f"Created infant: {new_infant!r}")

    return new_infant
