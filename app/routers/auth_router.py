from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.user_schema import UserCreate, UserOut, TokenResponse
from app.services.user_service import UserService
from app.core.security import create_email_token, create_access_token, verify_password, decode_token, get_current_user
from app.utils.email_utils import send_email_async
from app.core.config import get_settings
from app.core.enums import RoleEnum, TokenAudience

settings = get_settings()

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def signup(
    payload : UserCreate,
    background_tasks : BackgroundTasks,
    db : AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        user = await user_service.create_user(payload)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    
    # create secrets

    token = create_email_token(str(user.id))
    verify_url = f"{settings.BACKEND_URL}auth/verify?token={token}"

    background_tasks.add_task(
        send_email_async,
        user.email,
        "Verify your YouCanBeChef account",
        f"Click here to verify your account: {verify_url}"
    )

    return user

@router.get("/verify")
async def verify(token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token, TokenAudience.EMAIL_VERIFICATION)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    service = UserService(db)
    repo = service.repo
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Already verified"}
    await service.mark_verified(user)
    return {"message": "Email verified"}


@router.post("/login",response_model=TokenResponse)
async def login(form_data : OAuth2PasswordRequestForm = Depends(),db : AsyncSession = Depends(get_db)):
    repo = UserService(db).repo
    user = await repo.get_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    token = create_access_token(str(user.id),user.role)

    return {"access_token": token, "token_type": "bearer"}



