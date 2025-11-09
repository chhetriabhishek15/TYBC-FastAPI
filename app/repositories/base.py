from typing import Generic, TypeVar, Type
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")

class BaseRepository(Generic[T]):

    def __init__(self,model:Type[T],db:AsyncSession):
        self.model = model
        self.db = db

    async def get_all(self):
        q = select(self.model)
        res = await self.db.execute(q)
        return res.scalars().all()
    
    async def get_by_id(self,_id:uuid4):
        q = select(self.model).filter(self.model.id==_id)
        res = await self.db.execute(q)
        return res.scalar_one_or_none()
    
    async def add(self,instance: T):
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
    
    async def delete(self,instance: T):
        await self.db.delete(instance)
        await self.db.commit()