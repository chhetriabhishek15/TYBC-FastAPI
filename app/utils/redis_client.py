from redis.asyncio import Redis
from app.core.config import get_settings

settings = get_settings()

_redis : Redis = None

def init_redis_pool() -> Redis:
    global _redis

    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis

def get_redis() -> Redis:

    if _redis is None:
        raise RuntimeError("Redis not initialized, call init_redis_pool in startup")
    
    return _redis