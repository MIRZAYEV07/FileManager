from fastapi import APIRouter, HTTPException, status

from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from database.hash import Hash
from models import User
from auth import oauth2
from schemas import UserBaseSchema
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from database.database import get_db


router = APIRouter(
    tags=['authentication']
)


@router.post('/token')
def get_token(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).options(joinedload(User.companies),joinedload(User.role),joinedload(User.company)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password")

    access_token = oauth2.create_access_token(data={'sub': user.username, 'scopes': request.scopes})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user.id,
        'username': user.username,
        "user_info": UserBaseSchema(**user.__dict__)
    }
