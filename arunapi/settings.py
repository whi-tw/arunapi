from typing import Union

from pydantic import AnyUrl, BaseSettings, RedisDsn


class MemDsn(AnyUrl):
    allowed_schemes = {"mem"}
    host_required = False


class Settings(BaseSettings):
    environment: str = "prod"

    redis_url: RedisDsn = None
    memory_cache_url: MemDsn = "mem://?size=500"

    @property
    def cache_url(self) -> Union[RedisDsn, MemDsn]:
        return self.redis_url if self.redis_url else self.memory_cache_url
