import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship, AutoString


##############################################################################
# Token models
##############################################################################

class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenData(SQLModel):
    user_id: int | None = None


##############################################################################
# User models
##############################################################################

class UserBase(SQLModel):
    email: EmailStr = Field(sa_type=AutoString)
    disabled: Optional[bool] = Field(default=None)


class User(UserBase, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    access_key: str = Field(unique=True, index=True)


class UserCreate(UserBase):
    access_key: str


class UserUpdate(UserBase):
    email: Optional[EmailStr]
    access_key: Optional[str]
    disabled: Optional[bool]


class UserRead(UserBase):
    user_id: int


##############################################################################
# Infant models
##############################################################################

class InfantBase(SQLModel):
    full_name: str
    birth_date: datetime.date
    due_date: datetime.date
    nhi_number: str = Field(unique=True, description="The NHI number must be unique", index=True)


class Infant(InfantBase, table=True):
    infant_id: Optional[int] = Field(default=None, primary_key=True)

    consents: list["Consent"] = Relationship(back_populates="infant")
    videos: list["Video"] = Relationship(back_populates="infant")


class InfantCreate(InfantBase):
    pass


class InfantUpdate(SQLModel):
    full_name: Optional[str]
    birth_date: Optional[datetime.date]
    due_date: Optional[datetime.date]
    nhi_number: Optional[str]


class InfantOut(InfantBase):
    infant_id: int


##############################################################################
# Consent models
##############################################################################

class ConsentBase(SQLModel):
    consent_giver_name: Optional[str] = Field(default=None)
    consent_giver_email: Optional[EmailStr] = Field(default=None, sa_type=AutoString)
    collected_physically: bool = Field(
        default=False,
        description="An electronic consent is not required because a physical consent exists",
    )


class Consent(ConsentBase, table=True):
    consent_id: Optional[int] = Field(default=None, primary_key=True)
    infant_id: int = Field(foreign_key="infant.infant_id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    created_by: int = Field(default=None, foreign_key="user.user_id")

    infant: Infant = Relationship(back_populates="consents")


class ConsentCreateViaNHI(ConsentBase):
    nhi_number: str


class ConsentCreate(ConsentBase):
    infant_id: int


class ConsentUpdate(SQLModel):
    consent_giver_name: Optional[str]
    collected_physically: Optional[bool]


class ConsentOut(ConsentBase):
    consent_id: int
    infant_id: int
    created_at: datetime.datetime
    created_by: int


##############################################################################
# Video models
##############################################################################

class VideoBase(SQLModel):
    video_name: str = Field(unique=True, index=True)
    sha256sum: str = Field(min_length=64, max_length=64)


class Video(VideoBase, table=True):
    video_id: Optional[int] = Field(default=None, primary_key=True)
    infant_id: int = Field(foreign_key="infant.infant_id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    created_by: int = Field(foreign_key="user.user_id")
    video_size: Optional[int] = Field(default=None)

    infant: Infant = Relationship(back_populates="videos")


class VideoCreate(VideoBase):
    infant_id: int


class VideoCreateViaNHI(VideoBase):
    nhi_number: str


class VideoUpdate(SQLModel):
    video_size: Optional[int]


class VideoOut(VideoBase):
    video_id: int
    infant_id: int
    created_at: datetime.datetime
    created_by: int
    video_size: int
