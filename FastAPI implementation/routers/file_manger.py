import os

from fastapi import APIRouter, Depends, HTTPException, FileResponse, File, UploadFile, Security
from sqlalchemy.orm import Session
from models import User, File as FileModel, Permission, Folder
import uuid
from minio import Minio
from database.minio_client import get_minio_client
from database.database import get_db, get_mongo_db
from auth.oauth2 import get_current_user
from schemas.users import UserBaseSchema
from utilities import generate_md5


BUCKET_NAME = "filestorage"
ENDPOINT = os.getenv("MINIO_ENDPOINT")
from utilities import generate_md5

minio_client = get_minio_client()
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

router = APIRouter(
    prefix='/file_manager',
    tags=['file_manager']
)


def get_minio_file_url(bucket_name: str, file_name: str) -> str:
    minio_client = get_minio_client()
    return minio_client.presigned_get_object(bucket_name, file_name)

async def upload_file_to_minio(file: UploadFile, bucket_name: str, object_name: str, minio_client: Minio):
    minio_client.put_object(bucket_name, object_name, file.file, file.content_length)
    return get_minio_file_url(bucket_name, object_name)


@router.post("/folders/")
async def create_folder(name: str, db: Session = Depends(get_db), 
                        current_user: UserBaseSchema = Security(get_current_user, scopes=['user:write'])):
    new_folder = Folder(name=name, owner=current_user)
    db.add(new_folder)
    db.commit()
    return {"id": new_folder.id, "name": new_folder.name}


@router.put("/folders/{folder_id}/rename")
async def rename_folder(folder_id: int, new_name: str, db: Session = Depends(get_db), 
                        current_user: UserBaseSchema = Security(get_current_user, scopes=['user:write'])):
    folder = db.query(Folder).filter_by(id=folder_id, owner_id=current_user.id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder.name = new_name
    db.commit()
    return {"id": folder.id, "new_name": new_name}


@router.post("/upload/{folder_id}/")
async def upload_file_to_folder(folder_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: UserBaseSchema = Security(get_current_user, scopes=['user:write']), minio_client: Minio = Depends(get_minio_client)):
    folder = db.query(Folder).filter_by(id=folder_id, owner_id=current_user.id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    bucket_name = "filestorage"
    unique_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    object_name = f"{folder.name}/{generate_md5(unique_id)}.{file_extension}"

    file_url = await upload_file_to_minio(file, bucket_name, object_name, minio_client)

    new_file = FileModel(filename=file.filename, url=file_url, folder=folder, owner=current_user)
    db.add(new_file)
    db.commit()

    permission = Permission(file_id=new_file.id, user_id=current_user.id, can_read=True, can_change=True)
    db.add(permission)
    db.commit()

    return {"info": f"file '{file.filename}' saved in folder '{folder.name}'", "file_url": file_url}


@router.post("/share/{file_id}")
async def share_file(file_id: int, target_user_id: int, can_read: bool, can_change: bool, 
                     db: Session = Depends(get_db),
                     current_user: UserBaseSchema = Security(get_current_user, scopes=['user:write'])):
    permission_check = db.query(Permission).filter(Permission.file_id == file_id, Permission.user_id == current_user.id, Permission.can_change == True).first()
    if not permission_check:
        raise HTTPException(status_code=403, detail="Access denied")

    permission = db.query(Permission).filter(Permission.file_id == file_id, Permission.user_id == target_user_id).first()
    if not permission:
        permission = Permission(file_id=file_id, user_id=target_user_id, can_read=can_read, can_change=can_change)
        db.add(permission)
    else:
        permission.can_read = can_read
        permission.can_change = can_change
    db.commit()
    return {"info": f"Permissions updated for user {target_user_id}"}


@router.put("/folders/{folder_id}/rename")
async def rename_folder(folder_id: int, new_name: str, db: Session = Depends(get_db),
                        current_user: UserBaseSchema = Security(get_current_user, scopes=['user:write'])):
    folder = db.query(Folder).filter_by(id=folder_id, owner_id=current_user.id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    folder.name = new_name
    db.commit()
    return {"id": folder.id, "new_name": new_name}


@router.get("/folders/{folder_id}/files")
async def get_files_in_folder(folder_id: int, db: Session = Depends(get_db),
                              current_user: UserBaseSchema = Security(get_current_user, scopes=['user:read'])):
    folder = db.query(Folder).filter_by(id=folder_id, owner_id=current_user.id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    files = db.query(FileModel).filter_by(folder_id=folder_id).all()
    return {"folder": folder.name, "files": [file.filename for file in files]}


@router.get("/search/")
async def search_files(query: str, folder_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    files = db.query(FileModel).join(Folder, Permission).filter(
        Folder.id == folder_id,
        Folder.owner_id == current_user.id,
        FileModel.filename.ilike(f"%{query}%"),
        Permission.user_id == current_user.id,
        Permission.can_read == True
    ).all()
    return {"files": [file.filename for file in files]}


@router.delete("/delete/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db),
                      current_user: UserBaseSchema = Security(get_current_user, scopes=['user:write']),
                      minio_client: Minio = Depends(get_minio_client)):
    file_record = db.query(FileModel).join(Permission).filter(
        FileModel.id == file_id,
        Permission.file_id == file_id,
        Permission.user_id == current_user.id,
        Permission.can_change == True
    ).first()
    if not file_record:
        raise HTTPException(status_code=403, detail="Access denied")

    object_name = file_record.path.split("/")[-1]
    minio_client.remove_object(BUCKET_NAME, object_name)

    db.delete(file_record)
    db.commit()
    return {"info": f"file '{file_record.filename}' deleted"}
