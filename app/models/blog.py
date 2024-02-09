from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Boolean, Float, DateTime, UUID,
    ForeignKey, CheckConstraint,
    func,
    select, and_, delete, update
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from . import Base
from app.models.user import User

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, unique=True, index=True, nullable=False)
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Define the relationship using string names
    posts = relationship("Post", foreign_keys="Post.blog_id")
    
    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        new_blog = cls(**kwargs)
        db.add(new_blog)
        await db.commit()
        await db.refresh(new_blog)
        return new_blog
    
    @classmethod
    async def find_by_id(cls, db: AsyncSession, id: UUID):
        query = select(cls).where(cls.id== id)
        result = await db.execute(query)
        return result.scalars().first()
            
    @classmethod
    async def find_all_by_username(cls, db: AsyncSession, username: str):
        user = await User.find_by_username(db, username=username)
        query = select(cls).where(and_(cls.created_by == user.id, cls.is_deleted.is_(False)))
        result = await db.execute(query)
        return result.scalars().all()
        
    @classmethod
    async def find_all_by_email(cls, db: AsyncSession, email: str):
        user = await User.find_by_email(db, email=email)
        query = select(cls).where(and_(cls.created_by == user.id, cls.is_deleted.is_(False)))
        result = await db.execute(query)
        return result.scalars().all()
        
    @classmethod
    async def patch(cls, db: AsyncSession, id: UUID, **kwargs):
        # Fetch the user from the database
        blog = await cls.find_by_id(db, id)
        if blog is None:
            return None

        # Update only the provided fields in kwargs
        for key, value in kwargs.items():
            setattr(blog, key, value)

        await db.commit()
        await db.refresh(blog)
        return blog
    

    @classmethod
    async def delete(cls, db: AsyncSession, id: UUID) -> Optional["Blog"]:
        # Fetch the blog from the database
        blog = await cls.find_by_id(db, id)
        if blog is None:
            return None

        # Refresh the blog object
        blog.is_deleted = True
        await db.commit()
        await db.refresh(blog)
        return blog
    
    @classmethod
    async def check_availability(cls, db: AsyncSession, created_by: UUID, title: str):
        query = select(cls).where(and_(cls.created_by == created_by, cls.title == title, cls.is_deleted.is_(False)))
        result = await db.execute(query)
        return result.scalars().first() is None