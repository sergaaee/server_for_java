import datetime
from hashlib import sha256 as hasher
from config import get_settings
from sqlalchemy.orm import Session
from . import models
from .schemas import UserCreate, TaskCreate, TaskDelete, TaskUpdate


settings = get_settings()


def create_user(db: Session, user: UserCreate):
    salt = settings.SALT
    db_user = models.Users(username=user.username,
                           password=hasher((salt + user.password + salt).encode()).hexdigest(),
                           reg_date=datetime.datetime.now(),
                           email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return "Success"


def auth_new_session(fingerprint: str, username: str, db: Session):
    user_id = db.query(models.Users).filter(models.Users.username == username).first().id
    refresh_token = hasher(username.encode()).hexdigest()
    data = models.Sessions(user_id=user_id,
                           fingerprint=fingerprint,
                           refresh_token=refresh_token,
                           created_at=datetime.datetime.now())
    db.add(data)
    db.commit()
    db.refresh(data)
    return refresh_token


def refresh_tokens(fingerprint: str, refresh_token: str, db: Session):
    try:
        db_fingerprint = db.query(models.Sessions).filter(models.Sessions.refresh_token == refresh_token).first().fingerprint
    except AttributeError:
        return False
    if fingerprint != db_fingerprint:
        db.query(models.Sessions).filter(models.Sessions.refresh_token == refresh_token).delete()
        db.commit()
        return False
    created_at = db.query(models.Sessions).filter(models.Sessions.refresh_token == refresh_token).filter(models.Sessions.fingerprint == fingerprint).first().created_at
    if (datetime.datetime.now().date() - created_at.date()).days > 90:
        return False
    return True


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.Users).filter(models.Users.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.Users).filter(models.Users.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).filter(models.Users.email == email).first()


def create_task(db: Session, task: TaskCreate, user_id: int):
    check_task = db.query(models.Tasks)\
        .filter(models.Tasks.user_id == user_id)\
        .filter(models.Tasks.name == task.name)\
        .first()
    if check_task is None:
        data = models.Tasks(user_id=user_id,
                            name=task.name,
                            start_time=task.start_time,
                            end_time=task.end_time,
                            description=task.description,
                            created_at=datetime.datetime.now()
                            )
        db.add(data)
        db.commit()
        db.refresh(data)
        return "Success"
    return None


def update_task(db: Session, task: TaskUpdate, user_id: int):
    check_task = db.query(models.Tasks).filter(models.Tasks.user_id == user_id).filter(
        models.Tasks.name == task.name).first()
    if check_task is None:
        db.query(models.Tasks).filter(models.Tasks.user_id == user_id).filter(models.Tasks.name == task.name).update({"name": task.new_name, "start_time": task.new_stime, "end_time": task.new_etime, "description": task.new_desc})
        db.commit()
        return "Success"
    return None


def delete_task(db: Session, task: TaskDelete, user_id: int):
    db.query(models.Tasks).filter(models.Tasks.user_id == user_id).filter(models.Tasks.name == task.name).delete()
    db.commit()
    return "Success"


def get_tasks(db: Session, user_id: int):
    return db.query(models.Tasks).filter(models.Tasks.user_id == user_id).all()
