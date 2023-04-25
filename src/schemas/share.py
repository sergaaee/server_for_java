from typing import Optional

from pydantic import BaseModel


class Share(BaseModel):
    user_id: Optional[int]
    friend_id: Optional[int]
    task_id: Optional[int]


class ShareNew(Share):
    user_id: int
    friend_id: int
    task_id: int


class ShareDelete(BaseModel):
    user_id: int
    task_id: int
