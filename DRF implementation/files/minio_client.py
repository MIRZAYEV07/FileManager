from minio import Minio
import os

def minio_client():
    client = Minio(
        os.getenv('MINIO_HOST'),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key=os.getenv('MINIO_SECRET_KEY'),
        secure=True
    )
    return client

def upload_file(file_obj, object_name):
    client = minio_client()
    client.put_object('mybucket', object_name, file_obj, file_obj.size)
    return f"{client._endpoint_url}/mybucket/{object_name}"