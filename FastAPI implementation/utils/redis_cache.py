import json
import aioredis
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

REDIS_URL = os.getenv("REDIS_URL")


async def get_redis_connection():
    return await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def get_cached_data(key: str):
    redis = await get_redis_connection()
    data = await redis.get(key)
    await redis.close()
    if data:
        return json.loads(data)
    return None


async def set_cached_data(key: str, value, expiration_time: int = 300):
    redis = await get_redis_connection()
    value_str = json.dumps(value,  indent=4, sort_keys=True, default=str)
    await redis.set(key, value_str, ex=expiration_time)
    await redis.close()
