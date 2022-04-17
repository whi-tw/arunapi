import os
import redis

REDIS = redis.from_url(os.environ.get("REDIS_URL"))
