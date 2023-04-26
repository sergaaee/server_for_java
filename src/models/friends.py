from sqlalchemy import Column, Integer, String, TIMESTAMP
from database import Base


class Friends(Base):
    __tablename__ = "Friends"

    id = Column(Integer, primary_key=True, unique=True)
    user_id: Column[Integer] = Column(Integer)
    friend_id = Column(Integer)
    status = Column(String)
    created_at = Column(TIMESTAMP)