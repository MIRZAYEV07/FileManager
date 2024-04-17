import os
from typing import Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from fastapi import HTTPException, status, Security
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from jose import jwt
from jose.exceptions import JWTError
from pydantic import ValidationError

from database import db_user
from database.database import get_db
from schemas import TokenData, UserBaseSchema

scopes = {
    "me": "Read information about the current user.",
    "admin:read": "Read information about the admin.",
    "admin:write": "Write information about the admin.",
    "user:read": "Read information about the user.",
    "user:write": "Write information about the user.",

}

load_dotenv(find_dotenv())
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=scopes)
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 262800))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])

        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError) as e:
        raise credentials_exception
    user = db_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception



    for scope in security_scopes.scopes:

        if scope not in token_data.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not enough permissions')
    # return UserDisplay(**user.__dict__)
    return user


def get_current_active_user(current_user: UserBaseSchema = Security(get_current_user, scopes=["me"])):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user


def get_admin(current_user: UserBaseSchema = Security(get_current_user, scopes=["admin:read admin:write"])):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Not admin')
    return current_user


def get_current_user_with_token(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = db_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not enough permissions')

    return user, token
