from fastapi import Depends, FastAPI, HTTPException, status, Header
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from config import get_settings
from . import crud, models
from .database import SessionLocal, engine
from .schemas import TaskUpdate, TaskCreate, TaskDelete, UserCreate, UserData, UserAuth, FriendDelete, ShareDelete
models.Base.metadata.create_all(bind=engine)

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokens/new")

app = FastAPI()


# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_pass(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = crud.hasher((settings.SALT + password + settings.SALT).encode()).hexdigest()
    db_user = crud.get_user_by_username(db, username=username)
    if hashed_password != db_user.password:
        return False
    return True


def auth_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        return False
    if not verify_pass(username, password, db):
        return False
    return db_user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = crud.get_user_by_username(db, username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def check_user(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_user = crud.get_user_by_username(db, username=current_user.username)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Unknown user")
    return db_user


@app.post("/users", tags=["User"],)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_username = crud.get_user_by_username(db, username=user.username)
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_username:
        raise HTTPException(status_code=422, detail="Username already registered")
    elif db_user_email:
        raise HTTPException(status_code=422, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/tokens", tags=["token"], )
async def login_for_new_session(fingerprint: str = Header(), db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = crud.auth_new_session(fingerprint=fingerprint, username=form_data.username, db=db)
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/tokens/refresh", tags=["token"],)
async def refresh_tokens(fingerprint: str = Header(), refresh_token: str = Header(), db: Session = Depends(get_db)):

    if crud.refresh_tokens(fingerprint, refresh_token, db):
        user_id = db.query(models.Sessions).filter(models.Sessions.refresh_token == refresh_token).first().user_id
        username = db.query(models.Users).filter(models.Users.id == user_id).first().username
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/users", tags=["User"], )
async def full_user_data(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    user = check_user(db=db, current_user=current_user)
    tasks = crud.get_tasks(db=db, user_id=user.id)
    user.__delattr__("password")
    return user, tasks


@app.post("/tasks", tags=["Tasks"])
async def create_new_task(task: TaskCreate, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    result = crud.create_task(db=db, task=task, user_id=db_user.id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Name already exists",
        )
    return result


@app.get("/tasks", tags=["Tasks"])
async def get_tasks(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    user = check_user(db=db, current_user=current_user)
    tasks = crud.get_tasks(db=db, user_id=user.id)
    return [tasks]


@app.patch("/tasks", tags=["Tasks"])
async def update_task(task: TaskUpdate, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    result = crud.update_task(db=db, task=task, user_id=db_user.id)
    return result


@app.delete("/tasks", tags=["Tasks"])
async def delete_task(task: TaskDelete, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_user = check_user(db=db, current_user=current_user)
    return crud.delete_task(db=db, task=task, user_id=db_user.id)