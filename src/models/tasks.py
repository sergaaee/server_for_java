from sqlalchemy import Column, Integer, String, TIMESTAMP
from database import Base


class Tasks(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer)
    name = Column(String)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    description = Column(String)
    status = Column(String)
    created_at = Column(TIMESTAMP)
    sharing_from = Column(Integer)
    sharing_to = Column(Integer)
