from sqlalchemy.orm import Session
from schemas import UserCreate
from config import get_settings
from models import Users
from hashlib import sha256 as hasher
import datetime

settings = get_settings()


def create_user(db: Session, user: UserCreate):
    # Get salt from the settings
    salt = settings.SALT

    # Hash the password using the salt and store the user in the database
    db_user = Users(
        username=user.username,
        password=hasher((salt + user.password + salt).encode()).hexdigest(),
        reg_date=datetime.datetime.now(),
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return "Success"


def get_user_by_id(db: Session, user_id: int):
    # Get a user from the database by their ID
    return db.query(Users) \
        .filter(Users.id == user_id) \
        .first()


def get_user_by_username(db: Session, username: str):
    # Get a user from the database by their username
    return db.query(Users) \
        .filter(Users.username == username) \
        .first()


def get_user_by_email(db: Session, email: str):
    # Get a user from the database by their email address
    return db.query(Users) \
        .filter(Users.email == email) \
        .first()


def delete_user_by_email(db: Session, email: str):
    db.query(Users) \
        .filter(Users.email == email) \
        .delete()
    db.commit()
    return "Success"
