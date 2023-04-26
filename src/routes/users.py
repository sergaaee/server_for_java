from typing import List

from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from schemas import UserCreate, UserAuth, UserData, Task
from sqlalchemy.orm import Session
from database import get_db
from crud import (
    get_user_by_email,
    get_user_by_username,
    create_user,
    check_user,
    get_tasks,
    get_current_user
)

# Define a new router for user-related endpoints
router_users = APIRouter(prefix="/users")


# Define a new data model for a user with their associated tasks
class BaseUser(BaseModel):
    user: UserData
    tasks: List[Task]


# Endpoint to create a new user
@router_users.post("", tags=["User"], response_model=str)
async def create_a_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if a user with the given username or email already exists
    db_user_username = get_user_by_username(db, username=user.username)
    db_user_email = get_user_by_email(db, email=user.email)
    if db_user_username:
        raise HTTPException(status_code=422, detail="Username already registered")
    elif db_user_email:
        raise HTTPException(status_code=422, detail="Email already registered")
    # If the user doesn't already exist, create a new one
    return create_user(db=db, user=user)


# Endpoint to get a user with their associated tasks
@router_users.get("", tags=["User"], response_model=BaseUser)
async def user_with_tasks(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    # Check that the current user is valid and get their associated tasks
    user = check_user(db=db, current_user=current_user)
    tasks = get_tasks(db=db, user_id=user.id)
    # Remove the user's password from the returned data
    user.__delattr__("password")
    # Return the user and their associated tasks
    return user, tasks
