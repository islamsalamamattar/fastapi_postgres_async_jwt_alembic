from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, select, func, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from . import Base



class BlackListToken(Base):
    __tablename__ = "blacklisttokens"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    expire = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    
    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        token = cls(**kwargs)
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token
    
    @classmethod
    async def find_by_id(cls, db: AsyncSession, id: UUID):
        query = select(cls).where(cls.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def patch(cls, db: AsyncSession, id: UUID, **kwargs):
        # Fetch the user from the database
        token = await cls.get(db, id)
        if token is None:
            return None

        # Update only the provided fields in kwargs
        for key, value in kwargs.items():
            setattr(token, key, value)

        await db.commit()
        await db.refresh(token)
        return token