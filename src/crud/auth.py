from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from hashlib import sha256 as hasher
from crud import get_user_by_username
from sqlalchemy.orm import Session
from database import get_db
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from config import get_settings
from schemas import UserAuth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokens/new")
settings = get_settings()


def verify_pass(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = hasher((settings.SALT + password + settings.SALT).encode()).hexdigest()
    db_user = get_user_by_username(db, username=username)
    if hashed_password != db_user.password:
        return False
    return True


def auth_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=username)
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
        token_data = get_user_by_username(db, username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def check_user(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_user = get_user_by_username(db, username=current_user.username)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Unknown user")
    return db_user
