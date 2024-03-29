import logging
from datetime import datetime, timedelta
from typing import Any, Tuple, Union

from cashews import Cache as Cashews

from .settings import CacheSettings


class NotInCache(Exception):
    pass


class CacheSetFailed(Exception):
    pass


class Cache:
    def __init__(self, settings: CacheSettings) -> None:
        self.logger = logging.getLogger("cashews")
        self.cache = Cashews()
        self.settings = settings
        if settings.redis_url:
            self.cache.setup(settings.redis_url)
            self.logger.info(f"Redis cache Configured: '{settings.redis_url}'")
        elif settings.memory_cache_url:
            self.cache.setup(settings.memory_cache_url)
            self.logger.warning(
                f"Memory cache Configured: '{settings.memory_cache_url}'"
            )
        else:
            self.cache.disable()
            self.logger.warning("Cache Disabled")

    @staticmethod
    def build_key(key: str, namespace: str) -> str:
        return f"{namespace}.{key}"

    async def get_cache(self, key, namespace="") -> Tuple[Any, float]:
        key = self.build_key(key, namespace)
        res = await self.cache.get(key)
        expiry = await self.cache.get_expire(key)
        if not res:
            raise NotInCache
        return res, expiry

    async def set_cache(
        self,
        value,
        key: str,
        namespace="",
        ttl: Union[float, timedelta] = None,
    ) -> bool:
        return await self.cache.set(
            key=self.build_key(key, namespace), value=value, expire=ttl
        )

    async def health(self) -> str:
        key = value = datetime.now().isoformat()
        cache_key = self.build_key(key, namespace="healthcheck")
        await self.cache.set(key=cache_key, value=value)
        retr_value = await self.cache.get(cache_key)
        await self.cache.expire(cache_key, 1)
        if retr_value == value:
            return "OK"
        else:
            return "BAD"
