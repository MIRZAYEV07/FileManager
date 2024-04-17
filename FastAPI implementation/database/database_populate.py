from models import User
from sqlalchemy.orm import Session

from schemas import UserCreateSchema, UserUpdateSchema
from database.db_user import create as create_user

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def create_users(db: Session):
    create_user(db, UserCreateSchema(username=os.getenv("USERNAME"), email="some1@gmail.com",
                                     password=os.getenv("PASSWORD"), is_superuser=True))

