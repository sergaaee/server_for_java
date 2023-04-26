from fastapi import Depends, APIRouter, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from crud import auth_user, create_access_token, auth_new_session
from models import Sessions, Users
from config import get_settings
from datetime import timedelta

settings = get_settings()

router_tokens = APIRouter(prefix="/tokens")


@router_tokens.post("", tags=["token"], )
async def create_a_session(fingerprint: str = Header(), db: Session = Depends(get_db),
                           form_data: OAuth2PasswordRequestForm = Depends()):
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
    refresh_token = auth_new_session(fingerprint=fingerprint, username=form_data.username, db=db)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router_tokens.post("/refresh", tags=["token"], )
async def refresh_tokens(fingerprint: str = Header(), refresh_token: str = Header(), db: Session = Depends(get_db)):
    if refresh_tokens(fingerprint, refresh_token, db):
        user_id: int = db.query(Sessions).filter(Sessions.refresh_token == refresh_token).first().user_id
        username = db.query(Users).filter(Users.id == user_id).first().username
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
