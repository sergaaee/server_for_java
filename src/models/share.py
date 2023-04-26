from sqlalchemy import Column, Integer
from database import Base


class Share(Base):
    __tablename__ = "Share"

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer)
    friend_id = Column(Integer)
    task_id = Column(Integer)
