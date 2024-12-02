from fastapi import Request
import time
from redis import Redis
from kkdatad.utils.config import settings

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds

    async def is_rate_limited(self, key: str) -> bool:
        current = int(time.time())
        window_key = f"{key}:{current // self.window}"
        
        count = self.redis.get(window_key)
        if count is None:
            pipeline = self.redis.pipeline()
            pipeline.incr(window_key)
            pipeline.expire(window_key, self.window)
            count = pipeline.execute()[0]
        else:
            count = int(count)
            if count >= self.rate_limit:
                return True
            self.redis.incr(window_key)
        
        return False

rate_limiter = RateLimiter(Redis(
    host=settings.REDIS_DATABASE_HOST,
    port=settings.REDIS_DATABASE_PORT
)) 