import datetime

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from crud import (
    get_current_user,
    check_user,
    create_task,
    update_task,
    delete_task,
    get_tasks
)
from database import get_db
from schemas import UserAuth, TaskCreate, TaskDelete, TaskUpdate

router_tasks = APIRouter(prefix="/tasks")


@router_tasks.post("", tags=["Tasks"], response_model=str)
async def create_a_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        current_user: UserAuth = Depends(get_current_user)
):
    try:
        datetime.datetime.strptime(str(task.start_time), "%Y-%m-%d %H:%M:%S")
        datetime.datetime.strptime(str(task.end_time), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect datetime format",
        )
    # Check if the user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    # Create the task
    result = create_task(db=db, task=task, user_id=db_user.id)

    # Raise an HTTPException if the task could not be created
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Name already exists",
        )

    return result


@router_tasks.get("", tags=["Tasks"])
async def get_all_tasks(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    # Check if the user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    tasks = get_tasks(db=db, user_id=db_user.id)

    return [tasks]


@router_tasks.patch("", tags=["Tasks"], response_model=str)
async def update_a_task(
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    try:
        datetime.datetime.strptime(str(task.new_stime), "%Y-%m-%d %H:%M:%S")
        datetime.datetime.strptime(str(task.new_etime), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect datetime format",
        )
    # Check if the user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    result = update_task(db=db, task=task, user_id=db_user.id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return result


@router_tasks.delete("", tags=["Tasks"], response_model=str)
async def delete_a_task(
    task: TaskDelete,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    # Check if the user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    # Delete the task
    result = delete_task(db=db, task=task, user_id=db_user.id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return result
