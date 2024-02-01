from fastapi import APIRouter

from tinymotion_backend.api.api_v1.endpoints import login
from tinymotion_backend.api.api_v1.endpoints import video

api_v1_router = APIRouter()
api_v1_router.include_router(login.router, prefix="/token", tags=["token"])
#api_v1_router.include_router(video.router, prefix="/videos", tags=["videos"])
