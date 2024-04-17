from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum, Time, Date
from sqlalchemy.orm import relationship

from models import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_superuser = Column(Boolean, default=False)
    image = Column(String)
    folders = relationship("Folder", back_populates="owner")
    files = relationship("File", back_populates="owner")
    permissions = relationship("Permission", back_populates="user")


