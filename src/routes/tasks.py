from typing import List
from fastapi import Depends, APIRouter, HTTPException, status
from schemas import UserAuth, TaskCreate, TaskDelete, TaskUpdate
from sqlalchemy.orm import Session
from database import get_db
from crud import (
    get_current_user,
    check_user,
    create_task,
    update_task,
    delete_task,
    get_tasks
)

router_tasks = APIRouter(prefix="/tasks")


@router_tasks.post("", tags=["Tasks"], response_model=str)
async def create_a_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """
    Create a new task for the authenticated user.

    Returns:
        str: "Success" if everything is okay.
    """
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
    """
    Get all tasks of the authenticated user.

    Returns:
        dict: A dictionary with all user's tasks
    """
    # Check if the user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    # Get all tasks of the authenticated user
    tasks = get_tasks(db=db, user_id=db_user.id)

    return [tasks]


@router_tasks.patch("", tags=["Tasks"], response_model=str)
async def update_a_task(
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """
    Update an existing task of the authenticated user.

    Returns:
        str: "Success" if everything is okay.
    """
    # Check if the user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    # Update the task
    result = update_task(db=db, task=task, user_id=db_user.id)

    return result


@router_tasks.delete("", tags=["Tasks"], response_model=str)
async def delete_a_task(
    task: TaskDelete,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """
    Delete an existing task of the authenticated user.

    Returns:
        str: "Success" if everything is okay.
    """
    # Check if the user is authenticated
    db_user = check_user(db=db, current_user=current_user)

    # Delete the task
    result = delete_task(db=db, task=task, user_id=db_user.id)

    return result
