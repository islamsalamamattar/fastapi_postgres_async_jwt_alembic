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
from app.models.blog import Blog
from app.models.user import User

class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, unique=True, index=True, nullable=False)
    body = Column(String, nullable=False)
    blog_id = Column(UUID, ForeignKey("blogs.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Define the relationship using string names
    #blog = relationship("Blog", back_populates="posts")
    
    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        new_post = cls(**kwargs)
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post
    
    @classmethod
    async def find_by_id(cls, db: AsyncSession, id: UUID):
        query = select(cls).where(cls.id== id)
        result = await db.execute(query)
        return result.scalars().first()
            
    @classmethod
    async def find_all_by_username(cls, db: AsyncSession, username: str):
        user = await User.find_by_username(db, username=username)
        query = select(cls).join(Blog).where(and_(Blog.created_by == user.id, cls.is_deleted.is_(False)))
        result = await db.execute(query)
        return result.scalars().all()
        
    @classmethod
    async def find_all_titles_by_blog(cls, db: AsyncSession, blog_id: UUID) -> List[str]:
        query = select(cls.title).where(cls.blog_id == blog_id)
        result = await db.execute(query)
        return result.scalars().all() or ["No Posts"]
            
    @classmethod
    async def patch(cls, db: AsyncSession, id: UUID, **kwargs):
        # Fetch the user from the database
        post = await cls.find_by_id(db, id)
        if post is None:
            return None

        # Update only the provided fields in kwargs
        for key, value in kwargs.items():
            setattr(post, key, value)

        await db.commit()
        await db.refresh(post)
        return post
    

    @classmethod
    async def delete(cls, db: AsyncSession, id: UUID) -> Optional["Blog"]:
        # Fetch the post from the database
        post = await cls.find_by_id(db, id)
        if post is None:
            return None

        # Refresh the post object
        post.is_deleted = True
        await db.commit()
        await db.refresh(post)
        return post
    
    @classmethod
    async def check_availability(cls, db: AsyncSession, blog_id: UUID, title: str):
        query = select(cls).where(and_(cls.blog_id == blog_id, cls.title == title, cls.is_deleted.is_(False)))
        result = await db.execute(query)
        return result.scalars().first() is None