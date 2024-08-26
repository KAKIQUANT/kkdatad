from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from database import get_financial_data

cache = Cache(Cache.MEMORY, serializer=PickleSerializer(), ttl=60)  # Cache for 60 seconds

@cached(cache=cache)
async def get_cached_data(query: str):
    return await get_financial_data(query)
