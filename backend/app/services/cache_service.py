import redis
from app.core.config import settings

class CacheService:
    def __init__(self):
        try:
            self.client = redis.Redis.from_url(settings.redis_url)
        except:
            self.client = None

    def get(self, key: str):
        if self.client:
            return self.client.get(key)
        return None

    def set(self, key: str, value: str, ttl=3600):
        if self.client:
            self.client.setex(key, ttl, value)