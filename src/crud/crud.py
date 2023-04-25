import datetime
from hashlib import sha256 as hasher
from config import get_settings
from sqlalchemy.orm import Session
import models
from schemas import UserCreate, TaskCreate, TaskDelete, TaskUpdate, FriendNew, FriendConfirm, FriendDelete, ShareNew

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
        db_fingerprint = db.query(models.Sessions) \
            .filter(models.Sessions.refresh_token == refresh_token) \
            .first() \
            .fingerprint
    except AttributeError:
        return False
    if fingerprint != db_fingerprint:
        db.query(models.Sessions) \
            .filter(models.Sessions.refresh_token == refresh_token) \
            .delete()
        db.commit()
        return False
    created_at = db.query(models.Sessions) \
        .filter(models.Sessions.refresh_token == refresh_token) \
        .filter(models.Sessions.fingerprint == fingerprint) \
        .first() \
        .created_at
    if (datetime.datetime.now().date() - created_at.date()).days > 90:
        return False
    return True


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.Users) \
        .filter(models.Users.id == user_id) \
        .first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.Users) \
        .filter(models.Users.username == username) \
        .first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users) \
        .filter(models.Users.email == email) \
        .first()


def create_task(db: Session, task: TaskCreate, user_id: int):
    check_task = db.query(models.Tasks) \
        .filter(models.Tasks.user_id == user_id) \
        .filter(models.Tasks.name == task.name) \
        .first()
    if check_task is None:
        data = models.Tasks(user_id=user_id,
                            name=task.name,
                            start_time=task.start_time,
                            end_time=task.end_time,
                            description=task.description,
                            status=task.status,
                            created_at=task.created_at,
                            sharing_to=task.sharing_to,
                            sharing_from=task.sharing_from
                            )
        db.add(data)
        db.commit()
        db.refresh(data)
        return "Success"
    return


def update_task(db: Session, task: TaskUpdate, user_id: int):
    db.query(models.Tasks) \
        .filter(models.Tasks.user_id == user_id) \
        .filter(models.Tasks.name == task.name) \
        .update(dict(name=task.new_name, start_time=task.new_stime, end_time=task.new_etime, description=task.new_desc,
                     status=task.new_status))
    db.commit()
    return "Success"


def delete_task(db: Session, task: TaskDelete, user_id: int):
    db.query(models.Tasks) \
        .filter(models.Tasks.user_id == user_id) \
        .filter(models.Tasks.name == task.name) \
        .delete()
    db.commit()
    return "Success"


def get_tasks(db: Session, user_id: int):
    tasks = db.query(models.Tasks) \
        .filter(models.Tasks.user_id == user_id) \
        .order_by(models.Tasks.status.desc()) \
        .order_by(models.Tasks.start_time.asc()) \
        .all()
    return tasks


def add_friend(db: Session, friend: FriendNew, user_id: int):
    user = get_user_by_id(db=db, user_id=friend.friend_id)
    if user is None:
        return
    check_friendship1 = db.query(models.Friends) \
        .filter(models.Friends.user_id == user_id) \
        .filter(models.Friends.friend_id == friend.friend_id) \
        .all()
    check_friendship2 = db.query(models.Friends) \
        .filter(models.Friends.friend_id == user_id) \
        .filter(models.Friends.user_id == friend.friend_id) \
        .all()
    if check_friendship1 or check_friendship2 or user_id == friend.friend_id:
        return "Found"
    data = models.Friends(
        user_id=user_id,
        friend_id=friend.friend_id,
        status="pending",
        created_at=friend.created_at
    )
    db.add(data)
    db.commit()
    return "Success"


def confirm_friend(db: Session, friend: FriendConfirm, user_id: int):
    db.query(models.Friends) \
        .filter(models.Friends.friend_id == user_id) \
        .filter(models.Friends.user_id == friend.friend_id) \
        .update(dict(status="added", created_at=friend.created_at))
    db.commit()
    data = models.Friends(
        user_id=user_id,
        friend_id=friend.friend_id,
        status="added",
        created_at=friend.created_at
    )
    db.add(data)
    db.commit()
    return "Success"


def get_friend_list(db: Session, user_id: int):
    confirmed_friends = db.query(models.Friends) \
        .filter(models.Friends.user_id == user_id) \
        .filter(models.Friends.status == "added") \
        .all()
    pending_to_user = db.query(models.Friends) \
        .filter(models.Friends.friend_id == user_id) \
        .filter(models.Friends.status == "pending") \
        .all()
    pending_from_user = db.query(models.Friends) \
        .filter(models.Friends.user_id == user_id) \
        .filter(models.Friends.status == "pending") \
        .all()
    return [confirmed_friends, pending_to_user, pending_from_user]


def delete_friend(db: Session, user_id: int, friend: FriendDelete):
    db.query(models.Friends) \
        .filter(models.Friends.user_id == user_id) \
        .filter(models.Friends.friend_id == friend.friend_id) \
        .delete()
    db.commit()
    db.query(models.Friends) \
        .filter(models.Friends.friend_id == user_id) \
        .filter(models.Friends.user_id == friend.friend_id) \
        .delete()
    db.commit()
    return "Success"


def add_task_to_friend(db: Session, user_id: int, friend_id: int, task: TaskCreate):
    check_task = db.query(models.Tasks) \
        .filter(models.Tasks.user_id == friend_id) \
        .filter(models.Tasks.name == task.name) \
        .first()
    if check_task is None:
        data = models.Tasks(user_id=friend_id,
                            name=task.name,
                            start_time=task.start_time,
                            end_time=task.end_time,
                            description=task.description,
                            status="*",
                            created_at=task.created_at,
                            sharing_from=user_id,
                            sharing_to=task.sharing_to
                            )
        db.add(data)
        db.commit()
        db.refresh(data)
        return "Success"
    return
