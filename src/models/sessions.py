from sqlalchemy import Column, Integer, String, TIMESTAMP
from database import Base


class Sessions(Base):
    __tablename__ = "Sessions"

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer)
    fingerprint = Column(String)
    refresh_token = Column(String)
    created_at = Column(TIMESTAMP)