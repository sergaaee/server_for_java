from fastapi import Depends, APIRouter, HTTPException, status
from schemas import UserAuth, TaskCreate, TaskDelete, TaskUpdate
from sqlalchemy.orm import Session
from database import get_db
from crud import get_current_user, check_user, create_task, update_task, delete_task, get_tasks

router_tasks = APIRouter(prefix="/tasks")


@router_tasks.post("", tags=["Tasks"])
async def create_a_task(task: TaskCreate, db: Session = Depends(get_db),
                        current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    result = create_task(db=db, task=task, user_id=db_user.id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Name already exists",
        )
    return result


@router_tasks.get("", tags=["Tasks"])
async def all_tasks(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    user = check_user(db=db, current_user=current_user)
    tasks = get_tasks(db=db, user_id=user.id)
    return [tasks]


@router_tasks.patch("", tags=["Tasks"])
async def update_a_task(task: TaskUpdate, db: Session = Depends(get_db),
                        current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    result = update_task(db=db, task=task, user_id=db_user.id)
    return result


@router_tasks.delete("", tags=["Tasks"])
async def delete_a_task(task: TaskDelete, db: Session = Depends(get_db),
                        current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    return delete_task(db=db, task=task, user_id=db_user.id)
