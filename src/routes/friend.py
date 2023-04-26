from fastapi import Depends, APIRouter, HTTPException, status, Header
from schemas import UserAuth, TaskCreate
from sqlalchemy.orm import Session
from database import get_db
from crud import get_current_user, check_user, add_friend, get_friend_list, confirm_friend, delete_friend, get_tasks, \
    add_task_to_friend
from models import Friends
from schemas import FriendNew, FriendDelete, FriendConfirm

router_friend = APIRouter(prefix="/friend")


@router_friend.post("", tags=["Friends"])
async def add_a_friend(friend: FriendNew, db: Session = Depends(get_db),
                       current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    result = add_friend(db=db, friend=friend, user_id=db_user.id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    elif result == "Found":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Connection already exists",
        )
    else:
        return "Success"


@router_friend.get("", tags=["Friends"])
async def friend_list(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    return get_friend_list(db=db, user_id=db_user.id)


@router_friend.patch("", tags=["Friends"])
async def confirm_a_friend(friend: FriendConfirm, db: Session = Depends(get_db),
                           current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    return confirm_friend(db=db, friend=friend, user_id=db_user.id)


@router_friend.delete("", tags=["Friends"])
async def delete_a_friend(friend: FriendDelete, db: Session = Depends(get_db),
                          current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    return delete_friend(db=db, friend=friend, user_id=db_user.id)


@router_friend.get("/tasks", tags=["Friends", "Tasks"])
async def friend_tasks(friend_id: int = Header(),
                       db: Session = Depends(get_db),
                       current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    check_friendship = db.query(Friends) \
        .filter(Friends.user_id == db_user.id) \
        .filter(Friends.friend_id == friend_id) \
        .all()
    if check_friendship:
        return [get_tasks(db=db, user_id=friend_id)]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong",
        )


@router_friend.post("/tasks", tags=["Friends", "Tasks"])
async def create_a_task_with_a_friend(task: TaskCreate,
                                      friend_id: int = Header(),
                                      db: Session = Depends(get_db),
                                      current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    return add_task_to_friend(db=db, user_id=db_user.id, friend_id=friend_id, task=task)
