import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from tinymotion_backend.core.config import settings
from tinymotion_backend._version import __version__ as tinymotion_backend_version
from tinymotion_backend.api.api_v1.api import api_v1_router


logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s|%(name)s|%(levelname)s|%(message)s',
)
logging.getLogger('tinymotion_backend').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ensure video library exists
    os.makedirs(settings.VIDEO_LIBRARY_PATH, exist_ok=True)

    # make sure secrets were set
    if settings.ACCESS_TOKEN_SECRET_KEY is None:
        raise RuntimeError("ACCESS_TOKEN_SECRET_KEY has not been set")
    if settings.REFRESH_TOKEN_SECRET_KEY is None:
        raise RuntimeError("REFRESH_TOKEN_SECRET_KEY has not been set")
    if settings.DATABASE_SECRET_KEY is None:
        raise RuntimeError("DATABASE_SECRET_KEY has not been set")
    if settings.VIDEO_SECRET_KEY is None:
        raise RuntimeError("VIDEO_SECRET_KEY has not been set")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=tinymotion_backend_version,
    lifespan=lifespan,
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
