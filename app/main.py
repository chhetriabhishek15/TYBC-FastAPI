from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from redis.asyncio import Redis
from app.database.session import engine
from app.database.base import Base, SCHEMA_CREATION_ENVS
from app.core.config import get_settings
from app.utils.redis_client import get_redis, init_redis_pool
from app.routers import api_routers

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    if settings.ENV in SCHEMA_CREATION_ENVS:
        print(f"[{settings.ENV.upper()}]: Auto-creating database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    await init_redis_pool()

    yield 
    
    print("Application shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

@app.get("/",tags=["health"])
async def health():
    return "Healthy"

@app.get("/test-cache",tags=["redis"])
async def redis_health(
    redis : Redis = Depends(get_redis)
):
    await redis.set("health_check", "ok")

    status = await redis.get("health_check")

    return {"status": "ok", "check_value": status}

app.include_router(api_routers)