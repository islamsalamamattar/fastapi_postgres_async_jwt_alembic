from pydantic import BaseModel, UUID4, validator, EmailStr
from typing import Any, Optional, List
from datetime import datetime

class BlogBase(BaseModel):
    title: str

class Blog(BlogBase):
    id: UUID4
    created_by: UUID4
    created_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class BlogCreate(BlogBase):
    pass

class BlogPatch(BaseModel):
    title: Optional[str] = None

class BlogsList(BaseModel):
    blogs: List[Blog]

class BlogDetails(BaseModel):
    blog: Blog
    post_titles: List[str]

