from typing import Optional

from pydantic import BaseModel
from pydantic.validators import datetime


class FriendBase(BaseModel):
    user_id: Optional[int]
    friend_id: Optional[int]
    status: Optional[str]
    created_at: Optional[datetime]


class FriendNew(BaseModel):
    friend_id: int


class FriendConfirm(BaseModel):
    friend_id: int


class FriendDelete(BaseModel):
    friend_id: int


class FriendTasks(BaseModel):
    friend_id: int
