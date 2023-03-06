from typing import Optional

from pydantic import BaseModel


class Share(BaseModel):
    user_id: Optional[int]
    task_id: Optional[int]


class ShareNew(Share):
    user_id: int
    task_id: int


class ShareDelete(Share):
    user_id: int
    task_id: int
