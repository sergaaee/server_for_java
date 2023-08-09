from typing import List

from fastapi import Depends, APIRouter, HTTPException, status, Header

from sqlalchemy.orm import Session

from database import get_db
from crud import (
    get_current_user, check_user, add_friend, get_friend_list, confirm_friend,
    delete_friend, get_tasks, add_task_to_friend
)
from models import Friends
from schemas import UserAuth, TaskCreate, FriendNew, FriendDelete, FriendConfirm, FriendBase

router_friend = APIRouter(prefix="/friend")


# Endpoint to add a friend
@router_friend.post("", tags=["Friends"], response_model=str)
async def add_a_friend_by_id(friend: FriendNew, db: Session = Depends(get_db),
                             current_user: UserAuth = Depends(get_current_user)):
    # Check if the current user is authenticated
    db_user = check_user(db=db, current_user=current_user)
    # Call the 'add_friend' function to add the friend to the current user's friend list
    result = add_friend(db=db, friend=friend, user_id=db_user.id)
    # Check if the result is None (i.e., the friend was not found)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    # Check if the result is "Found" (i.e., the friend is already in the current user's friend list)
    elif result == "Found":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Connection already exists",
        )
    # If the friend was successfully added to the current user's friend list, return a success message
    else:
        return "Success"


# Endpoint to get the list of friends
@router_friend.get("", tags=["Friends"])
async def friend_list(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    # Check if the current user is authenticated
    db_user = check_user(db=db, current_user=current_user)
    # Call the 'get_friend_list' function to get the list of friends of the current user
    return get_friend_list(db=db, user_id=db_user.id)


# Endpoint to confirm a friend
@router_friend.patch("", tags=["Friends"], response_model=str)
async def confirm_a_friend(friend: FriendConfirm, db: Session = Depends(get_db),
                           current_user: UserAuth = Depends(get_current_user)):
    # Check if the current user is authenticated
    db_user = check_user(db=db, current_user=current_user)
    # Call the 'confirm_friend' function to confirm the friendship
    return confirm_friend(db=db, friend=friend, user_id=db_user.id)


# Endpoint to delete a friend
@router_friend.delete("", tags=["Friends"], response_model=str)
async def delete_a_friend_by_id(friend: FriendDelete, db: Session = Depends(get_db),
                                current_user: UserAuth = Depends(get_current_user)):
    # Check if the current user is authenticated
    db_user = check_user(db=db, current_user=current_user)
    # Call the 'delete_friend' function to delete the friend from the current user's friend list
    return delete_friend(db=db, friend=friend, user_id=db_user.id)


# Endpoint to get the tasks of a friend
@router_friend.get("/tasks", tags=["Friends", "Tasks"])
async def friend_tasks(friend_id: str = Header(),
                       db: Session = Depends(get_db),
                       current_user: UserAuth = Depends(get_current_user)):
    # Check if the current user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    # Check if there is a friendship between the current user and the friend
    check_friendship = db.query(Friends) \
        .filter(Friends.user_id == db_user.id) \
        .filter(Friends.friend_id == int(friend_id)) \
        .all()

    # If there is a friendship, return the friend's tasks
    if check_friendship:
        return [get_tasks(db=db, user_id=int(friend_id))]

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You aren't friends",
        )


@router_friend.post("/tasks", tags=["Friends", "Tasks"], response_model=str)
async def create_a_task_with_a_friend(task: TaskCreate,
                                      friend_id: int = Header(),
                                      db: Session = Depends(get_db),
                                      current_user: UserAuth = Depends(get_current_user)):
    # Check if the current user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    # Add a task to a friend's to-do list
    return add_task_to_friend(db=db, user_id=db_user.id, friend_id=friend_id, task=task)
