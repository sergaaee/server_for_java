from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic.validators import datetime


class User(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]


class UserCreate(User):
    username: str
    password: str
    email: EmailStr


class UserData(BaseModel):
    username: str
    email: EmailStr
    reg_date: datetime

    class Config:
        orm_mode = True


class UserAuth(BaseModel):
    username: str
    password: str
