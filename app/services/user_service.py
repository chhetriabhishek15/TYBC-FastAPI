from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserService:
    def __init__(self,db:AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self,payload:UserCreate)-> User:
        existing_user = await self.repo.get_by_email(payload.email)
        if existing_user:
            raise ValueError("Email already registered")
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            role=payload.role
        )
        return await self.repo.add(user)
    
    async def mark_verified(self,user:User):
        user.is_verified=True

        await self.repo.db.commit()
        await self.repo.db.refresh(user)

        return user