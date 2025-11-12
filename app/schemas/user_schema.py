from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

from app.core.enums import RoleEnum


class UserCreate(BaseModel):
    email : EmailStr
    password : str
    full_name : Optional[str]
    role : RoleEnum = RoleEnum.CUSTOMER

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str]
    role: RoleEnum
    is_verified: bool
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"