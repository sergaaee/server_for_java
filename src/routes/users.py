from fastapi import Depends, APIRouter, HTTPException
from schemas import UserCreate, UserAuth
from sqlalchemy.orm import Session
from database import get_db
from crud import get_user_by_email, get_user_by_username, create_user, check_user, get_tasks, get_current_user


router_users = APIRouter(prefix="/users")


@router_users.post("", tags=["User"], )
async def create_a_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_username = get_user_by_username(db, username=user.username)
    db_user_email = get_user_by_email(db, email=user.email)
    if db_user_username:
        raise HTTPException(status_code=422, detail="Username already registered")
    elif db_user_email:
        raise HTTPException(status_code=422, detail="Email already registered")
    return create_user(db=db, user=user)


@router_users.get("", tags=["User"], )
async def get_a_user(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    user = check_user(db=db, current_user=current_user)
    tasks = get_tasks(db=db, user_id=user.id)
    user.__delattr__("password")
    return user, tasks