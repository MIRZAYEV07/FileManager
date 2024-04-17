import imp
from typing import List, Optional
from pydantic import BaseModel, validator
from fastapi import Form, HTTPException, status
# import sqlalchemy import
from sqlalchemy import Enum
from datetime import date

from fastapi import HTTPException, status
from typing import Annotated

from typing_extensions import Annotated, Doc


class UserBaseSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None

    @classmethod
    def as_form(cls, username: str = Form(...), first_name: str = Form(None),
                last_name: str = Form(None), middle_name: str = Form(None), phone: str = Form(None),
                email: str = Form(None), password: str = Form(None),
                ):
        return cls(username=username, first_name=first_name, last_name=last_name,
                   middle_name=middle_name, phone=phone, email=email,  password=password)


class UserManipulationSchema(BaseModel):
    username: str
    email: str
    password: str
    is_superuser: bool = False

    @validator('username')
    def username_must_contain_at_least_4_characters(cls, v):
        if len(v) < 4:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Username must be at least 4 characters long')
        return v

    @validator('password')
    def password_must_contain_at_least_8_characters(cls, v):
        if len(v) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Password must be at least 8 characters long')
        return v

    @validator('email')
    def email_validator(cls, v):
        if '@' not in v:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email must be a valid email address')
        return v


class UserCreateSchema(UserManipulationSchema):
    pass


class UserUpdateSchema(UserManipulationSchema):
    pass


