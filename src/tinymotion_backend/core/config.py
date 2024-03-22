import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet


class Settings(BaseSettings):
    ACCESS_TOKEN_SECRET_KEY: str = secrets.token_urlsafe(32)
    REFRESH_TOKEN_SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 8

    PROJECT_NAME: str = "TinyMotion"
    API_V1_STR: str = "/v1"

    FILE_CHUNK_SIZE_BYTES: int = 1024 * 1024 * 10  # default to 10 MB

    DATABASE_URI: str = "sqlite:///tinymotion.db"
    DATABASE_SECRET_KEY: str = Fernet.generate_key().decode('ascii')

    VIDEO_LIBRARY_PATH: str = "./videos"
    VIDEO_SECRET_KEY: str = Fernet.generate_key().decode('ascii')


    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="TINYMOTION_", env_file=".tinymotion.env")


settings = Settings()
