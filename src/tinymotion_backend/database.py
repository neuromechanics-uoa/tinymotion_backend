from sqlmodel import SQLModel, create_engine

from tinymotion_backend.core.config import settings


connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URI, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
