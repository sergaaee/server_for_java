from sqlalchemy.orm import Session
from schemas import TaskCreate, TaskUpdate, TaskDelete
from models import Tasks


def create_task(db: Session, task: TaskCreate, user_id: int):
    # Check if the task already exists
    check_task = db.query(Tasks) \
        .filter(Tasks.user_id == user_id) \
        .filter(Tasks.name == task.name) \
        .first()
    if check_task is None:
        # Create a new task
        data = Tasks(user_id=user_id,
                     name=task.name,
                     start_time=task.start_time,
                     end_time=task.end_time,
                     description=task.description,
                     status=task.status,
                     created_at=task.created_at,
                     sharing_to=task.sharing_to,
                     sharing_from=task.sharing_from
                     )
        db.add(data)
        db.commit()
        db.refresh(data)
        return "Success"
    # Return None if the task already exists
    return


def update_task(db: Session, task: TaskUpdate, user_id: int):
    # Update the task with the new values
    check_task = db.query(Tasks) \
        .filter(Tasks.user_id == user_id) \
        .filter(Tasks.name == task.name) \
        .first()
    if check_task is None:
        return
    db.query(Tasks) \
        .filter(Tasks.user_id == user_id) \
        .filter(Tasks.name == task.name) \
        .update(dict(name=task.new_name, start_time=task.new_stime, end_time=task.new_etime, description=task.new_desc,
                     status=task.new_status))
    db.commit()
    return "Success"


def delete_task(db: Session, task: TaskDelete, user_id: int):
    # Delete the task
    check_task = db.query(Tasks) \
        .filter(Tasks.user_id == user_id) \
        .filter(Tasks.name == task.name) \
        .first()
    if check_task is None:
        return
    db.query(Tasks) \
        .filter(Tasks.user_id == user_id) \
        .filter(Tasks.name == task.name) \
        .delete()
    db.commit()
    return "Success"


def get_tasks(db: Session, user_id: int):
    # Retrieve all tasks for a given user and order them by status and start time
    tasks = db.query(Tasks) \
        .filter(Tasks.user_id == user_id) \
        .order_by(Tasks.status.desc()) \
        .order_by(Tasks.start_time.asc()) \
        .all()
    return tasks


def add_task_to_friend(db: Session, user_id: int, friend_id: int, task: TaskCreate):
    # Check if the task already exists for the friend
    check_task = db.query(Tasks) \
        .filter(Tasks.user_id == friend_id) \
        .filter(Tasks.name == task.name) \
        .first()
    if check_task is None:
        # Create a new task for the friend with the status "*" means pending
        data = Tasks(user_id=friend_id,
                     name=task.name,
                     start_time=task.start_time,
                     end_time=task.end_time,
                     description=task.description,
                     status="*",
                     created_at=task.created_at,
                     sharing_from=user_id,
                     sharing_to=task.sharing_to
                     )
        db.add(data)
        db.commit()
        db.refresh(data)
        return "Success"
    # Return None if the task already exists
    return
