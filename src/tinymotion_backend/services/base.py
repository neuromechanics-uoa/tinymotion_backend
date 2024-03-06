from typing import Any, Generic, Optional, Type, TypeVar

import sqlalchemy
from sqlmodel import Session, SQLModel

from tinymotion_backend.core.exc import UniqueConstraintError


ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: Session, created_by: int | None = None):
        self.model = model
        self.db_session = db_session
        self.created_by = created_by

    def get(self, id: Any) -> Optional[ModelType]:
        obj: Optional[ModelType] = self.db_session.get(self.model, id)

        return obj

    def list(self) -> list[ModelType]:
        objs: list[ModelType] = self.db_session.query(self.model).all()

        return objs

    def create(self, obj: CreateSchemaType) -> ModelType:
        # construct the db model object
        db_obj: ModelType = self.model(**obj.model_dump(mode='python'))

        # add created by if exists
        if self.created_by is not None:
            db_obj.created_by = self.created_by

        # add to database
        self.db_session.add(db_obj)
        try:
            self.db_session.commit()
            self.db_session.refresh(db_obj)
        except sqlalchemy.exc.IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e) or "UNIQUE constraint failed" in str(e):
                raise UniqueConstraintError(str(e))
            else:
                raise e

        return db_obj

    def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        db_obj = self.get(id)
        for column, value in obj.model_dump(mode="json", exclude_unset=True).items():
            setattr(db_obj, column, value)
        self.db_session.commit()

        return db_obj

    def delete(self, id: Any) -> None:
        db_obj = self.db_session.get(self.model, id)
        self.db_session.delete(db_obj)
        self.db_session.commit()

        return db_obj
