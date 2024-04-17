import os
import random
from typing import List, Optional
import requests
from io import BytesIO
from fastapi import APIRouter, Depends, Security, Body
from sqlalchemy.orm import Session
from models import User
from database import db_user
from database.database import get_db
from schemas import (UserSchema, UserCreateSchema,
                     UserBaseSchema)
from typing import Annotated
from fastapi import File, UploadFile
from auth.oauth2 import get_current_user

import io
from datetime import timedelta, datetime
import json
from utils.pagination import CustomPage
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import HTTPException, status
import uuid


import secrets
import string

BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
ENTPOINT = os.getenv("MINIO_ENDPOINT")
from database.minio_client import get_minio_client


router = APIRouter(
    prefix='/user',
    tags=['user']
)


@router.get('/detail/{user_id}', response_model=UserSchema)
def get_user_by_id(company_id: int, user_id: int, db: Session = Depends(get_db)):
    return db_user.get_user_by_id(db, user_id, company_id)


minio_client = get_minio_client()
MINIO_PROTOCOL = os.getenv("MINIO_PROTOCOL")
MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_BUCKET_NAME = "userdata"

if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
    minio_client.make_bucket(MINIO_BUCKET_NAME)




@router.post('', response_model=UserSchema, tags=['admin_user'])
def create(request: UserCreateSchema, db: Session = Depends(get_db)):
    return db_user.create(db, request)


@router.get("", response_model=CustomPage[UserSchema], tags=['admin_user'])
def get_all(db: Session = Depends(get_db), current_user: UserBaseSchema = Security(get_current_user)):
    query_set = db_user.get_super_user(db)
    return paginate(db, query_set)


@router.get('/me', response_model=UserSchema)
def get_me(db: Session = Depends(get_db), current_user: UserBaseSchema = Security(get_current_user)):
    return db_user.get_me(db, current_user)


@router.put('/change_password')
def change_password(new_password: str, db: Session = Depends(get_db),
                    current_user: UserSchema = Security(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_user.change_password(db, user, new_password)
    return user



def generate_random_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password


def generate_fake_phone_number(prefix="+998", length=9):
    """Generate a fake phone number with the given prefix and length for the number part."""
    number = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return prefix + number
