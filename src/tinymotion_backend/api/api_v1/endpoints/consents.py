import logging

from fastapi import APIRouter, Depends, HTTPException

from tinymotion_backend.api import deps
from tinymotion_backend import models
from tinymotion_backend.services.consent_service import ConsentService
from tinymotion_backend.core.exc import NotFoundError, InvalidInputError


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=models.ConsentOut,
    responses={
        400: {
            "description": "Bad Request Error",
            "content": {
                "application/json": {
                    "examples": {
                        "consent_giver_name": {
                            "value": {
                                "detail": "Must specify `consent_giver_name` when not specifying `collected_physically`",
                            },
                        },
                        "consent_giver_email": {
                            "value": {
                                "detail": "Must specify `consent_giver_email` when not specifying `collected_physically`",
                            },
                        },
                    },
                },
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Not authenticated"}}},
        },
        404: {
            "description": "Not Found Error",
            "content": {"application/json": {"example": {"detail": "An infant with the specified NHI number "
                                                         "does not exist"}}},
        },
    },
)
def create_consent(
    consent_in: models.ConsentCreateViaNHI,
    consent_service: ConsentService = Depends(deps.get_consent_service),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Create a consent linked to an infant

    """
    logger.debug(f"Creating consent: {consent_in!r}")
    logger.debug(f"Current user: {current_user!r}")

    try:
        new_consent = consent_service.create_using_nhi_number(consent_in)
    except NotFoundError as exc:
        logger.error(f"Error creating consent: {exc}")
        raise HTTPException(
            status_code=404,
            detail="An infant with the specified NHI number does not exist",
        )
    except InvalidInputError as exc:
        logger.error(f"Error creating consent: {exc}")
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    logger.debug(f"Created consent: {new_consent!r}")

    return new_consent
