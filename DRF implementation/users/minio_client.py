import os

from minio import Minio
from minio.error import S3Error

def minio_client():
    return Minio(
        os.getenv("MINIO_HOST"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False
    )