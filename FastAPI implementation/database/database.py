from functools import lru_cache
from typing import Iterator

from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
import motor.motor_asyncio

# load .env file from one directory up
load_dotenv(find_dotenv())
MONGO_DB_URL = os.environ.get("MONGODB_URL")

DATABASE_URL = os.getenv("POSTGRESS_URL")  # or other relevant config var
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()


def get_db() -> Iterator[Session]:
    """FastAPI dependency that provides a sqlalchemy session"""
    yield from _get_fastapi_sessionmaker().get_db()


@lru_cache()
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    """This function could be replaced with a global variable if preferred"""

    return FastAPISessionMaker(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False,
                            bind=create_engine(DATABASE_URL, pool_size=10, max_overflow=20))


def get_pg_db() -> Iterator[Session]:
    """FastAPI dependency that provides a sqlalchemy session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo_db():
    return motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)["file-manager"]


async def init_db():
    db = get_mongo_db()
    # Create the timeseries collection
    await db.create_collection(
        "file_recorder",
        timeseries={
            'timeField': 'timestamp',
            'metaField': 'device_id',
            'granularity': 'seconds'
        }
    )

    await db['file_recorder'].create_index([("timestamp", 1)])


