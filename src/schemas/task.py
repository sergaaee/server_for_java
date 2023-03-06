from typing import Optional

from pydantic import BaseModel
from pydantic.validators import datetime


class Task(BaseModel):
    name: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    description: Optional[str]


class TaskCreate(Task):
    name: str
    start_time: datetime
    end_time: datetime
    description: str


class TaskUpdate(BaseModel):
    name: str
    new_name: str
    new_stime: datetime
    new_etime: datetime
    new_desc: str


class TaskDelete(BaseModel):
    name: str
