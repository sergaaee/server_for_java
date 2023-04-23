from sqlalchemy import Column, Integer, String, TIMESTAMP
from database import Base


class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    reg_date = Column(TIMESTAMP)


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


class Friends(Base):
    __tablename__ = "Friends"

    id = Column(Integer, primary_key=True, unique=True)
    user_id: Column[int] = Column(Integer)
    friend_id = Column(Integer)
    status = Column(String)
    created_at = Column(TIMESTAMP)


class Share(Base):
    __tablename__ = "Share"

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer)
    task_id = Column(Integer)


class Sessions(Base):
    __tablename__ = "Sessions"

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer)
    fingerprint = Column(String)
    refresh_token = Column(String)
    created_at = Column(TIMESTAMP)
