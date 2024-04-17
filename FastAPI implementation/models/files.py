from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum, Time, Date
from sqlalchemy.orm import relationship

from models import BaseModel


class Folder(BaseModel):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="folders")

    files = relationship("File", back_populates="folder")


class File(BaseModel):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    filename = Column(String, index=True)
    path = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="files")
    folder_id = Column(Integer, ForeignKey('folders.id'))
    folder = relationship("Folder", back_populates="files")
    permissions = relationship("Permission", back_populates="file")
    versions = relationship("FileVersion", back_populates="file")

class Permission(BaseModel):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    can_read = Column(Boolean, default=False)
    can_change = Column(Boolean, default=False)
    file = relationship("File", back_populates="permissions")
    user = relationship("User", back_populates="permissions")

class FileVersion(BaseModel):
    __tablename__ = 'file_versions'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'))
    version_number = Column(Integer, default=1)
    file_path = Column(String)
    file = relationship("File", back_populates="versions")