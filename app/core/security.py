from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from pwdlib import PasswordHash
from jose import jwt, JWTError
from app.core.config import get_settings
from app.core.enums import TokenAudience, RoleEnum
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.repositories.user_repository import UserRepository
from app.database.session import AsyncSessionLocal
from app.utils.datetimeutil import utcnow

settings = get_settings()

password_hash = PasswordHash.recommended()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(pasword : str)->str:
    return password_hash.hash(pasword)

def verify_password(plain : str , hashed_passord : str) -> bool:
    return password_hash.verify(plain,hashed_passord)

def _create_jwt(
    subject : str, 
    delta : timedelta, 
    audience : TokenAudience, 
    extra_claims : Dict[str,Any] | None = None
) -> str :
    
    now = datetime.utcnow()
    payload = {
        "sub": str(subject),
        "iat": now,
        "nbf": now,
        "exp": now + delta,
        "aud": audience.value
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

    return token 

def create_access_token(subject : str, role : RoleEnum):
    return _create_jwt(subject,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ,TokenAudience.ACCESS,
        {"role":role.value}
    )

def create_email_token(subject : str):
    return _create_jwt(subject,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ,TokenAudience.EMAIL_VERIFICATION
    )


def decode_token(token : str, audience : TokenAudience):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM,audience=audience.value)
        return payload
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid or expired") from e

async def get_current_user(token : str = Depends(oauth2_schema)):

    payload = jwt.decode(token,TokenAudience.ACCESS)
    user_id = payload.get("sub")
    if not user_id :
        raise HTTPException(status_code=401, detail="Invalid token payload")

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
        return user
    

def require_role(role : RoleEnum):
    async def wrapper(current_user = Depends(get_current_user)):
        if current_user.get("role")!=role.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user   
    return wrapper
