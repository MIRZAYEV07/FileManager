import datetime
from typing import Optional, List
from sqlalchemy.sql import func
from dotenv.parser import Position
from sqlalchemy.orm.session import Session
from database.hash import Hash
from exceptions.user import UserWithUsernameAlreadyExistsException, UserNotFoundException, \
    UserWithEmailAlreadyExistsException
from models import User
from schemas import UserCreateSchema, UserUpdateSchema,  UserBaseSchema
from sqlalchemy import and_, or_
from sqlalchemy import desc

from fastapi import HTTPException, status, Form


def create(db: Session, request: UserCreateSchema):
    user = db.query(User).filter(User.username == request.username).first()
    if user:
        raise UserWithUsernameAlreadyExistsException(request.username)

    user = db.query(User).filter(User.email == request.email).first()
    if user:
        raise UserWithEmailAlreadyExistsException(request.email)

    new_user = User(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password),
        is_superuser=request.is_superuser,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def change_password(db: Session, user: UserBaseSchema, new_password: str):
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.password = Hash.bcrypt(new_password)
    db.commit()
    db.refresh(user)
    return user


def get_super_user(db: Session):
    query_set = db.query(User).filter(User.is_superuser == True)
    return query_set


def get_me(db: Session, user: UserBaseSchema):
    return user


def update(db: Session, request: UserUpdateSchema, current_user: UserBaseSchema):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise UserNotFoundException
    if user.username != request.username:
        user_with_username = db.query(User).filter(User.username == request.username).first()
        if user_with_username:
            raise UserWithUsernameAlreadyExistsException(request.username)
    if user.email != request.email:
        user_with_email = db.query(User).filter(User.email == request.email).first()
        if user_with_email:
            raise UserWithEmailAlreadyExistsException(request.email)
    user.username = request.username
    user.email = request.email
    user.password = Hash.bcrypt(request.password)
    user.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise UserNotFoundException
    return user


def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(and_(User.id == user_id)).first()
    if not user:
        raise UserNotFoundException
    return user


def get_users_by_username_list(db: Session, username_list: list):
    return db.query(User).filter(User.username.in_(username_list)).all()
