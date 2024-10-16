from sqlalchemy import event
from sqlmodel import SQLModel, create_engine

from tinymotion_backend.core.config import settings


connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URI, connect_args=connect_args)


# from https://stackoverflow.com/a/7831210
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


event.listen(engine, 'connect', _fk_pragma_on_connect)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
