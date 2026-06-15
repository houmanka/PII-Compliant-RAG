import logging

from temporalio import activity

from providers.cache_provider.contract import CacheProvider

logging.basicConfig(level=logging.INFO)

class CacheActivity:
    def __init__(self, cache_provider: CacheProvider) -> None:
        self.cache_provider = cache_provider

    @activity.defn
    async def delete_cache(self, key: str) -> None:
        logging.info(f"Deleting {key}")
        self.cache_provider.delete(key)