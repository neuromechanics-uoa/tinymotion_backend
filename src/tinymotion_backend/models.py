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
    access_key: str = Field(unique=True)


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
    nhi_number: str


class Infant(InfantBase, table=True):
    infant_id: Optional[int] = Field(default=None, primary_key=True)

    consent: "Consent" = Relationship(back_populates="infant")
    videos: list["Video"] = Relationship(back_populates="infant")


class InfantCreate(InfantBase):
    pass


class InfantRead(InfantBase):
    child_id: int


##############################################################################
# Consent models
##############################################################################

class ConsentBase(SQLModel):
    consent_giver_name: str
    created_at: datetime.datetime = Field(default=datetime.datetime.utcnow)
    created_by: int = Field(foreign_key="user.user_id")
    infant_id: int = Field(foreign_key="infant.infant_id")


class Consent(ConsentBase, table=True):
    consent_id: Optional[int] = Field(default=None, primary_key=True)

    infant: Infant = Relationship(back_populates="consent")


class ConsentCreate(ConsentBase):
    pass


class ConsentRead(SQLModel):
    consent_id: int


##############################################################################
# Video models
##############################################################################

class VideoBase(SQLModel):
    file_name: str
    sha256sum: str = Field(min_length=32, max_length=32)
    infant_id: int = Field(foreign_key="infant.infant_id")
    created_at: datetime.datetime = Field(default=datetime.datetime.utcnow)
    created_by: int = Field(foreign_key="user.user_id")


class Video(VideoBase, table=True):
    video_id: int = Field(default=None, primary_key=True)

    infant: Infant = Relationship(back_populates="videos")


class VideoCreate(VideoBase):
    pass


class VideoRead(SQLModel):
    video_id: int
