"""Redis cache utilities"""
import redis
import json
from typing import Any, Optional
from app.config import settings


class RedisCache:
    """Redis cache wrapper"""

    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized = json.dumps(value, default=str)
            self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.redis.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False


# Global cache instance
cache = RedisCache()
