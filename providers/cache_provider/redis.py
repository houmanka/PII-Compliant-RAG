from typing import Any
from config import Config
from providers.cache_provider.contract import CacheProvider
from redis import Redis

from providers.cache_provider.registry import register, CacheProviderKind


class RedisStorage(CacheProvider):
    def __init__(self, redis_connection: Redis):
        self.redis_connection = redis_connection

    def create(self, key: str, value: Any) -> None:
        self.redis_connection.set(key, value, nx=True)

    def exists(self, key: str) -> bool:
        return bool(self.redis_connection.exists(key))

    def delete(self, key: str) -> None:
        if self.exists(key):
            self.redis_connection.delete(key)

    def update(self, key: str, value: Any) -> None:
        self.redis_connection.set(key, value, xx=True)

    def fetch(self, key: str) -> Any:
        cached_data_bytes = self.redis_connection.get(key)
        if not cached_data_bytes:
            return None
        return cached_data_bytes.decode()


@register(CacheProviderKind.REDIS)
def create_cache(config: Config):
    redis_connection = Redis(host=config.redis_host, port=config.redis_port, decode_responses=False)
    return RedisStorage(redis_connection=redis_connection)