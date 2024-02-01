import logging

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

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=tinymotion_backend_version,
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
