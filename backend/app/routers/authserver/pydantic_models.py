from typing import List
from uuid import UUID

from pydantic import BaseModel

from libraries.utils.pydantic_base import CustomModel


class TokenModel(CustomModel):
    username: str
    password: str


class TokenResponseModel(BaseModel):
    access_token: UUID


class RolesResponseModel(BaseModel):
    roles_ids: List[int]


class UsersResponseModel(BaseModel):
    id: int
    username: str
