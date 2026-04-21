import os
from functools import lru_cache
from redis import Redis


@lru_cache
def get_redis() -> Redis:
    return Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )
