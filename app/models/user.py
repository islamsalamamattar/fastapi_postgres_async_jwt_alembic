from uuid import uuid4
from sqlalchemy import Column, String, select, DateTime, Boolean, func, ForeignKey, UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from app.utils.hash import verify_password,hash_password


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    password = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    is_disabled = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    blogs = relationship("Blog", foreign_keys="Blog.created_by")
    
    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        new_user = cls(**kwargs)
        new_user.password = hash_password(new_user.password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
        
    @classmethod
    async def find_by_id(cls, db: AsyncSession, id:UUID):
        query = select(cls).where(cls.id == id)
        result = await db.execute(query)
        return result.scalars().first()
            
    @classmethod
    async def find_by_username(cls, db: AsyncSession, username: str):
        query = select(cls).where(cls.username == username)
        result = await db.execute(query)
        return result.scalars().first()
        
    @classmethod
    async def find_by_email(cls, db: AsyncSession, email: str):
        query = select(cls).where(cls.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def authenticate(cls, db: AsyncSession, username: str, password: str):
        user = await cls.find_by_username(db=db, username=username)
        if not user or not verify_password(password, user.password):
            return False
        return user
        
    @classmethod
    async def patch(cls, db: AsyncSession, username: String, **kwargs):
        # Fetch the user from the database
        user = await cls.find_by_username(db, username)
        if user is None:
            return None

        # Update only the provided fields in kwargs
        for key, value in kwargs.items():
            setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user
    
    @classmethod
    async def delete(cls, db: AsyncSession, username: String):
        # Fetch the user from the database
        user = await cls.find_by_username(db, username)
        if user is None:
            return None

        # Set is_disabled to True and update the database
        user.is_disabled = True
        await db.commit()
        await db.refresh(user)
        return user
    
    @classmethod
    async def makesuper(cls, db: AsyncSession, username: String):
        # Fetch the user from the database
        user = await cls.find_by_username(db, username)
        if user is None:
            return None

        # Set is_disabled to True and update the database
        user.is_superuser = True
        await db.commit()
        await db.refresh(user)
        return user
