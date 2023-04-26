from sqlalchemy.orm import Session
from models import Sessions, Users
from hashlib import sha256 as hasher
import datetime


def auth_new_session(fingerprint: str, username: str, db: Session):
    # get user ID by username from database
    user_id = db.query(Users).filter(Users.username == username).first().id
    # generate refresh token using username
    refresh_token = hasher(username.encode()).hexdigest()
    # create new session and add to database
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
        # get fingerprint from database for given refresh token
        db_fingerprint = db.query(Sessions) \
            .filter(Sessions.refresh_token == refresh_token) \
            .first() \
            .fingerprint
    except AttributeError:
        # if session not found in database, return False
        return False
    # check if the given fingerprint matches the one in the database
    if fingerprint != db_fingerprint:
        # if fingerprints do not match, delete all sessions and return False
        db.query(Sessions) \
            .filter(Sessions.refresh_token == refresh_token) \
            .delete()
        db.commit()
        return False
    # get the creation date of the session from the database
    created_at = db.query(Sessions) \
        .filter(Sessions.refresh_token == refresh_token) \
        .filter(Sessions.fingerprint == fingerprint) \
        .first() \
        .created_at
    # check if the session is older than 90 days
    if (datetime.datetime.now().date() - created_at.date()).days > 90:
        return False
    # if session is valid, return True
    return True
