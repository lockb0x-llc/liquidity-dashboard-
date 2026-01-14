import os
from fastapi import Header, HTTPException, status
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
from src.config import API_KEY

async def verify_api_key(x_api_key: str = Header(...)):
    """
    Simple API key verification.
    """
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return x_api_key

async def init_cache():
    """
    Initialize FastAPI-Cache with Redis or InMemory backend.
    """
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            r = redis.from_url(redis_url, encoding="utf8", decode_responses=True)
            FastAPICache.init(RedisBackend(r), prefix="liquidity-api-cache")
            print(f"Initialized Redis cache at {redis_url}")
        except Exception as e:
            print(f"Failed to initialize Redis cache: {e}. Falling back to InMemory.")
            FastAPICache.init(InMemoryBackend(), prefix="liquidity-api-cache")
    else:
        FastAPICache.init(InMemoryBackend(), prefix="liquidity-api-cache")
        print("Initialized InMemory cache")
