import os
from datetime import datetime, timedelta
from typing import Any, Tuple, Union

from cashews import Cache as Cashews


class NotInCache(Exception):
    pass


class CacheSetFailed(Exception):
    pass


class Cache:
    def __init__(self) -> None:
        self.cache = Cashews()
        try:
            self.cache.setup(os.environ["REDIS_URL"])
        except KeyError:
            import logging

            uvicorn_logger = logging.getLogger("uvicorn")
            uvicorn_logger.warning('Environment variable "REDIS_URL" not set.')
            if os.getenv("MEMORY_CACHE"):
                self.cache.setup("mem://?size=500")
                uvicorn_logger.warning("Memory cache enabled by MEMORY_CACHE")
            else:
                self.cache.disable()
                uvicorn_logger.warning("Cache disabled.")

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
