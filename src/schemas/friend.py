from typing import Optional

from pydantic import BaseModel
from pydantic.validators import datetime


class Friend(BaseModel):
    user_id: Optional[int]
    friend_id: Optional[int]
    created_at: Optional[datetime]


class FriendNew(Friend):
    user_id: int
    friend_id: int
    created_at: datetime


class FriendDelete(BaseModel):
    user_id: int
    friend_id: int
