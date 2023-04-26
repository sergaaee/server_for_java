from sqlalchemy.orm import Session
from schemas import FriendNew, FriendConfirm, FriendDelete
from models import Friends
from crud import get_user_by_id


def add_friend(db: Session, friend: FriendNew, user_id: int):
    user = get_user_by_id(db=db, user_id=friend.friend_id)
    if user is None:
        return
    check_friendship1 = db.query(Friends) \
        .filter(Friends.user_id == user_id) \
        .filter(Friends.friend_id == friend.friend_id) \
        .all()
    check_friendship2 = db.query(Friends) \
        .filter(Friends.friend_id == user_id) \
        .filter(Friends.user_id == friend.friend_id) \
        .all()
    if check_friendship1 or check_friendship2 or user_id == friend.friend_id:
        return "Found"
    data = Friends(
        user_id=user_id,
        friend_id=friend.friend_id,
        status="pending",
        created_at=friend.created_at
    )
    db.add(data)
    db.commit()
    return "Success"


def confirm_friend(db: Session, friend: FriendConfirm, user_id: int):
    db.query(Friends) \
        .filter(Friends.friend_id == user_id) \
        .filter(Friends.user_id == friend.friend_id) \
        .update(dict(status="added", created_at=friend.created_at))
    db.commit()
    data = Friends(
        user_id=user_id,
        friend_id=friend.friend_id,
        status="added",
        created_at=friend.created_at
    )
    db.add(data)
    db.commit()
    return "Success"


def get_friend_list(db: Session, user_id: int):
    confirmed_friends = db.query(Friends) \
        .filter(Friends.user_id == user_id) \
        .filter(Friends.status == "added") \
        .all()
    pending_to_user = db.query(Friends) \
        .filter(Friends.friend_id == user_id) \
        .filter(Friends.status == "pending") \
        .all()
    pending_from_user = db.query(Friends) \
        .filter(Friends.user_id == user_id) \
        .filter(Friends.status == "pending") \
        .all()
    return [confirmed_friends, pending_to_user, pending_from_user]


def delete_friend(db: Session, user_id: int, friend: FriendDelete):
    db.query(Friends) \
        .filter(Friends.user_id == user_id) \
        .filter(Friends.friend_id == friend.friend_id) \
        .delete()
    db.commit()
    db.query(Friends) \
        .filter(Friends.friend_id == user_id) \
        .filter(Friends.user_id == friend.friend_id) \
        .delete()
    db.commit()
    return "Success"
