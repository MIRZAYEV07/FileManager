from functools import lru_cache

from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

# Initialize minioClient with an endpoint and access/secret keys.
minioClient = Minio(
    os.getenv("MINIO_ENDPOINT"),
    os.getenv("MINIO_ACCESS_KEY"),
    os.getenv("MINIO_SECRET_KEY"),
    region=os.getenv("AWS_STORAGE_REGION") if os.getenv("AWS_STORAGE_REGION") else "us-east-1",
    secure=False,
)


@lru_cache()
def get_minio_client():
    return minioClient
