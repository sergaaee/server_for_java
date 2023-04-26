from sqlalchemy.orm import Session
from models import Sessions, Users
from hashlib import sha256 as hasher
import datetime


def auth_new_session(fingerprint: str, username: str, db: Session):
    user_id = db.query(Users).filter(Users.username == username).first().id
    refresh_token = hasher(username.encode()).hexdigest()
    data = Sessions(user_id=user_id,
                           fingerprint=fingerprint,
                           refresh_token=refresh_token,
                           created_at=datetime.datetime.now())
    db.add(data)
    db.commit()
    db.refresh(data)
    return refresh_token


def refresh_tokens(fingerprint: str, refresh_token: str, db: Session):
    try:
        db_fingerprint = db.query(Sessions) \
            .filter(Sessions.refresh_token == refresh_token) \
            .first() \
            .fingerprint
    except AttributeError:
        return False
    if fingerprint != db_fingerprint:
        db.query(Sessions) \
            .filter(Sessions.refresh_token == refresh_token) \
            .delete()
        db.commit()
        return False
    created_at = db.query(Sessions) \
        .filter(Sessions.refresh_token == refresh_token) \
        .filter(Sessions.fingerprint == fingerprint) \
        .first() \
        .created_at
    if (datetime.datetime.now().date() - created_at.date()).days > 90:
        return False
    return True
