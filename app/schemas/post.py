from pydantic import BaseModel, UUID4, validator, EmailStr
from typing import Any, Optional
from datetime import datetime

class PostBase(BaseModel):
    title: str
    body: str

class Post(PostBase):
    id: UUID4
    blog: str
    created_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class PostCreate(PostBase):
    pass

class PostPatch(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None




