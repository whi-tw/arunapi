from typing import Optional, Tuple, Union

import semver
from pydantic import (
    AnyUrl,
    BaseModel,
    BaseSettings,
    EmailStr,
    HttpUrl,
    RedisDsn,
    validator,
)

from . import __version__


class MemDsn(AnyUrl):
    allowed_schemes = {"mem"}
    host_required = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def query_fields(self):
        fields_individual = self.query.split("&")
        return {field.split("=")[0]: field.split("=")[1] for field in fields_individual}

    @property
    def size(self):
        return int(self.query_fields["size"])


class AppContact(BaseModel):
    name: str = "Tom Whitwell"
    url: HttpUrl = "https://whi.tw/ell"
    email: EmailStr = "arunapi@mail.whi.tw"


class AppSettings(BaseSettings):
    version: str = __version__
    title: str = "Arun DC API"
    description: str = "The missing API for Arun District Council services"
    contact: AppContact = AppContact()
    docs_url: str = "/"

    @validator("version")
    def is_valid_semver(cls, v) -> str:
        try:
            semver.VersionInfo.parse(v)
            return v
        except ValueError as e:
            raise ValueError(f"{v} is not a valid semver") from e

    class Config:
        pass


class CacheSettings(BaseModel):
    redis_url: Optional[RedisDsn]
    memory_cache_url: MemDsn = "mem://?size=500"


class Settings(BaseSettings):
    environment: str = "prod"

    app: AppSettings = AppSettings()

    cache: CacheSettings = CacheSettings()

    class Config:
        env_nested_delimiter = "__"
