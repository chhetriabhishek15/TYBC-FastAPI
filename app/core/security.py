from datetime import timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import get_settings
from app.core.enums import TokenAudience, RoleEnum
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.repositories.user_repository import UserRepository
from app.database.session import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.datetimeutil import utcnow
import asyncio

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(pasword : str)->str:
    return pwd_context.hash(pasword)

def verify_password(plain : str , hashed_passord : str) -> bool:
    return pwd_context.verify(plain,hashed_passord)

def _create_jwt(
    subject : str, 
    delta : timedelta, 
    audience : TokenAudience, 
    extra_claims : Dict[str,Any] | None = None
) -> str :
    
    payload = {
        "sub" : str(subject),
        "iat" : utcnow,
        "nbf" : utcnow,
        "exp" : utcnow + delta,
        "aud" : audience.value
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

    return token 
