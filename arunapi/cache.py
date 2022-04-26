import os
from datetime import timedelta
from typing import Any, Tuple, Union

from cashews import Cache as Cashews


class NotInCache(Exception):
    pass


class CacheSetFailed(Exception):
    pass


class Cache:
    def __init__(self) -> None:
        self.cache = Cashews()
        self.cache.setup(os.getenv("REDIS_URL"))

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
