import datetime
from typing import List, Set, Optional
from uuid import UUID

from pydantic import BaseModel

from libraries.utils.pydantic_base import CustomModel


class BlogPatchModel(CustomModel):
    title: None | str = None
    description: None | str = None
    authors: None | str = None


class BlogInsertModel(CustomModel):
    title: str
    description: str
    authors: None | str = None


class BlogPatchResponseModel(BaseModel):
    status: str
    authors: List[int] | List
    updated_at: datetime.datetime
    title: str | None
    description: str | None


class BlogRetrieveResponseModel(BaseModel):
    id: UUID
    title: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner_id: int


class RetrieveResponseModel(BaseModel):
    blog: BlogRetrieveResponseModel
    authors: List[int] | List


class CreateResponseModel(BlogRetrieveResponseModel):
    authors: List[int] | List
