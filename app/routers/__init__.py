from fastapi import APIRouter
from app.routers.auth_router import router as auth_router

api_routers = APIRouter()

api_routers.include_router(auth_router,prefix="/auth", tags=["auth"])

