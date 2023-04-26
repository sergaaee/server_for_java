from database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP


class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    reg_date = Column(TIMESTAMP)
