import datetime
import uuid
import functools

import sqlalchemy
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy_utils import UUIDType
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship, AutoString, Column, ForeignKey

from tinymotion_backend.core.config import settings


##############################################################################
# Custom types to use in models
##############################################################################

class StringDate(sqlalchemy.types.TypeDecorator):
    """
    Helper that converts dates to string for storing in StringEncryptedType and
    back to date again when retrieving.

    """
    impl = sqlalchemy.types.Date

    def process_bind_param(self, value: datetime.date | str | None, dialect):
        """Convert to string if not string already"""
        if value is not None:
            if isinstance(value, datetime.date):
                value = value.isoformat()

        return value

    def process_result_value(self, value: datetime.date | str | None, dialect):
        """Convert back to date if not date already"""
        if value is not None:
            if isinstance(value, str):
                value = datetime.date.fromisoformat(value)

        return value


class DateTimeAware(sqlalchemy.types.TypeDecorator):
    """
    Helper that converts incoming DateTime to UTC and removes timezone for
    storing, then converts back to DateTime with timezone set to UTC when
    retrieving.

    """
    impl = sqlalchemy.types.DateTime

    def process_bind_param(self, value: datetime.datetime | None, dialect):
        """Convert to UTC and remove timeezone info"""
        if value is not None:
            value.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        return value

    def process_result_value(self, value: datetime.datetime | None, dialect):
        """Convert to datetime with timezone set to UTC"""
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)

        return value


##############################################################################
# Token models
##############################################################################

class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenData(SQLModel):
    user_id: uuid.UUID | None = None


##############################################################################
# User models
##############################################################################

class UserBase(SQLModel):
    disabled: bool | None = Field(default=None)


class User(UserBase, table=True):
    user_id: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
    ))
    email: EmailStr = Field(sa_column=Column(
        StringEncryptedType(
            sqlalchemy.VARCHAR,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        nullable=False,
    ))
    access_key: str = Field(sa_column=Column(
        StringEncryptedType(
            sqlalchemy.VARCHAR,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        index=True,
        unique=True,
        nullable=False,
    ))


class UserCreate(UserBase):
    email: EmailStr
    access_key: str


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None)
    access_key: str | None = None
    disabled: bool | None = None


class UserRead(UserBase):
    user_id: uuid.UUID
    email: EmailStr


##############################################################################
# Infant models
##############################################################################

class InfantBase(SQLModel):
    full_name: str
    birth_date: datetime.date
    due_date: datetime.date
    nhi_number: str = Field(unique=True, description="The NHI number must be unique", index=True)


class Infant(SQLModel, table=True):
    infant_id: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
    ))
    created_at: datetime.datetime = Field(
        sa_type=DateTimeAware,
        default_factory=functools.partial(datetime.datetime.now, tz=datetime.timezone.utc),
    )
    created_by: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        ForeignKey('user.user_id'),
        nullable=False,
    ))
    full_name: str = Field(sa_column=Column(
        StringEncryptedType(
            sqlalchemy.VARCHAR,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        nullable=False,
    ))
    nhi_number: str = Field(sa_column=Column(
        StringEncryptedType(
            sqlalchemy.VARCHAR,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        index=True,
        unique=True,
        nullable=False,
    ))
    birth_date: datetime.date = Field(sa_column=Column(
        StringEncryptedType(
            StringDate,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        nullable=False,
    ))
    due_date: datetime.date = Field(sa_column=Column(
        StringEncryptedType(
            StringDate,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        nullable=False,
    ))

    consents: list["Consent"] = Relationship(
        back_populates="infant",
        sa_relationship_kwargs={"cascade": "delete, delete-orphan"},
    )
    videos: list["Video"] = Relationship(
        back_populates="infant",
        sa_relationship_kwargs={"cascade": "delete, delete-orphan"},
    )


class InfantCreate(InfantBase):
    pass


class InfantUpdate(SQLModel):
    full_name: str | None = None
    birth_date: datetime.date | None = None
    due_date: datetime.date | None = None
    nhi_number: str | None = None


class InfantOut(InfantBase):
    infant_id: uuid.UUID
    created_at: datetime.datetime
    created_by: uuid.UUID


##############################################################################
# Consent models
##############################################################################

class ConsentBase(SQLModel):
    consent_giver_name: str | None = Field(default=None)
    consent_giver_email: EmailStr | None = Field(default=None, sa_type=AutoString)
    collected_physically: bool = Field(
        default=False,
        description="An electronic consent is not required because a physical consent exists",
    )


class Consent(SQLModel, table=True):
    consent_id: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
    ))
    infant_id: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        ForeignKey('infant.infant_id'),
        nullable=False,
    ))
    created_at: datetime.datetime = Field(
        sa_type=DateTimeAware,
        default_factory=functools.partial(datetime.datetime.now, tz=datetime.timezone.utc),
    )
    created_by: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        ForeignKey('user.user_id'),
        nullable=False,
    ))
    consent_giver_name: str = Field(sa_column=Column(
        StringEncryptedType(
            sqlalchemy.VARCHAR,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        nullable=True,
    ))
    consent_giver_email: EmailStr = Field(sa_column=Column(
        StringEncryptedType(
            sqlalchemy.VARCHAR,
            settings.DATABASE_SECRET_KEY,
            AesEngine,
            'pkcs5',
        ),
        nullable=True,
    ))
    collected_physically: bool = Field(
        default=False,
        description="An electronic consent is not required because a physical consent exists",
    )

    infant: Infant = Relationship(back_populates="consents")


class ConsentCreateViaNHI(ConsentBase):
    nhi_number: str


class ConsentCreate(ConsentBase):
    infant_id: uuid.UUID


class ConsentUpdate(SQLModel):
    consent_giver_name: str | None = None
    collected_physically: bool | None = None


class ConsentOut(ConsentBase):
    consent_id: uuid.UUID
    infant_id: uuid.UUID
    created_at: datetime.datetime
    created_by: uuid.UUID


##############################################################################
# Video models
##############################################################################

class VideoBase(SQLModel):
    video_name: str = Field(unique=True, index=True)
    sha256sum: str = Field(min_length=64, max_length=64)


class Video(VideoBase, table=True):
    video_id: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
    ))
    infant_id: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        ForeignKey('infant.infant_id'),
        nullable=False,
    ))
    created_at: datetime.datetime = Field(
        sa_type=DateTimeAware,
        default_factory=functools.partial(datetime.datetime.now, tz=datetime.timezone.utc),
    )
    created_by: uuid.UUID = Field(sa_column=Column(
        UUIDType(binary=False),
        ForeignKey('user.user_id'),
        nullable=False,
    ))
    video_size: int | None = Field(default=None)
    sha256sum_enc: str | None = Field(min_length=64, max_length=64)

    infant: Infant = Relationship(back_populates="videos")


class VideoCreate(VideoBase):
    infant_id: uuid.UUID


class VideoCreateViaNHI(VideoBase):
    nhi_number: str


class VideoUpdate(SQLModel):
    video_size: int | None = None
    sha256sum_enc: str | None = Field(min_length=64, max_length=64, default=None)


class VideoOut(VideoBase):
    video_id: uuid.UUID
    infant_id: uuid.UUID
    created_at: datetime.datetime
    created_by: uuid.UUID
    video_size: int
