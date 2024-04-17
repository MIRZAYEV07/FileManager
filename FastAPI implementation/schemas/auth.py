from typing import Union, List

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    user_id: Union[int, None] = None
    scopes: List[str] = []
