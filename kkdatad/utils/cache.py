from redis import Redis
from typing import Any, Optional
import pickle
import hashlib
from kkdatad.utils.config import settings

class QueryCache:
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_DATABASE_HOST,
            port=settings.REDIS_DATABASE_PORT
        )
        self.default_ttl = 3600  # 1 hour

    def _generate_key(self, query: str) -> str:
        """Generate cache key from SQL query"""
        return f"query:{hashlib.md5(query.encode()).hexdigest()}"

    async def get(self, query: str) -> Optional[Any]:
        """Get cached query result"""
        key = self._generate_key(query)
        data = self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None

    async def set(self, query: str, data: Any, ttl: int = None) -> None:
        """Cache query result"""
        key = self._generate_key(query)
        self.redis.setex(
            key,
            ttl or self.default_ttl,
            pickle.dumps(data)
        )

query_cache = QueryCache() 