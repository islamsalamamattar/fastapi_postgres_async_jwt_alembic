from pydantic import BaseModel, UUID4, validator, EmailStr
from typing import Any, Optional
from datetime import datetime

class BlogBase(BaseModel):
    title: str

class Blog(BlogBase):
    id: UUID4
    created_by: str
    created_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class BlogCreate(BlogBase):
    pass

class BlogPatch(BaseModel):
    title: Optional[str] = None




