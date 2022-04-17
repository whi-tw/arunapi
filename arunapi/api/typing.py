import json
from json import JSONEncoder
from datetime import datetime, timedelta
from typing import TypedDict, Union, Any, Tuple
from flask_restx import Model
from redis import Redis


from requests import Session


class BaseResponseClass:
    envelope = "result"


class NotInCache(Exception):
    pass


class CacheSetFailed(Exception):
    pass


class CacheMeta(TypedDict):
    ttl: int
    expires: datetime


class ApiSession:
    API_BASEURL: str
    session: Session
    response_model: Model
    redis: Redis

    class ResultEncoder(JSONEncoder):
        def default(self, o: Any) -> Any:
            if isinstance(o, datetime):
                return o.isoformat()

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def store_cache(
        self, key: str, data: Union[int, dict, str], expiry: datetime = None
    ) -> Tuple[Union[int, dict, str], CacheMeta]:
        data_encoded = json.dumps(data, cls=self.ResultEncoder)
        success = self.redis.set(key, data_encoded, exat=int(expiry.timestamp()))
        if success:
            cache_meta = CacheMeta(ttl=int(expiry.timestamp()), expires=expiry)
            return data, cache_meta
        raise CacheSetFailed

    def retrieve_cache(self, key: str) -> Tuple[Union[int, dict, str], CacheMeta]:
        data = self.redis.get(key)
        if data:
            ttl = self.redis.ttl(key)
            cache_meta = CacheMeta(
                ttl=ttl, expires=datetime.now() + timedelta(seconds=ttl)
            )
            return json.loads(data), cache_meta
        raise NotInCache
