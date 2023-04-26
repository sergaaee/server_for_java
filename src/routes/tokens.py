from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import get_settings
from crud import (
    auth_new_session,
    auth_user,
    create_access_token,
    refresh_tokens,
)
from database import get_db
from models import Sessions, Users

# Get the settings object from the configuration file
settings = get_settings()

# Create an instance of the APIRouter class
router_tokens = APIRouter(prefix="/tokens")


# Define a base token model
class BaseToken(BaseModel):
    access_token: str
    refresh_token: str


# Define an access token model
class AccessToken(BaseModel):
    access_token: str


# Define a route for creating a new session
@router_tokens.post("", tags=["token"], response_model=BaseToken)
async def create_a_session(
    fingerprint: str = Header(),
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    # Authenticate the user
    user = auth_user(form_data.username, form_data.password, db)
    if not user:
        # If the user is not authenticated, return an error response
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Set the expiration time for the access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create an access token
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Create a refresh token
    refresh_token = auth_new_session(
        fingerprint=fingerprint, username=form_data.username, db=db
    )
    # Return a response with the access token and refresh token
    return {"access_token": access_token, "refresh_token": refresh_token}


# Define a route for refreshing an access token
@router_tokens.post("/refresh", tags=["token"], response_model=AccessToken)
async def refresh_all_tokens(
    fingerprint: str = Header(),
    refresh_token: str = Header(),
    db: Session = Depends(get_db),
):
    # Check if the refresh token is valid
    if refresh_tokens(fingerprint, refresh_token, db):
        # If the refresh token is valid, get the user ID
        user_id: int = (
            db.query(Sessions).filter(Sessions.refresh_token == refresh_token).first().user_id
        )
        # Get the username associated with the user ID
        username = db.query(Users).filter(Users.id == user_id).first().username
        # Set the expiration time for the new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # Create a new access token
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        # Return a response with the new access token
        return {"access_token": access_token}
    else:
        # If the refresh token is not valid, return an error response
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
