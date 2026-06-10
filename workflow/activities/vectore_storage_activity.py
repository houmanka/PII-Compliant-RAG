"""
activity 1
1. based on the reference of the cache, return the vectors
2. set them up based on what Pinecone needs
3. Push your vectors to the pinecone storage
4. return the file_id, reference, and pinecone index

activity 2
1. use the file_id and update the database to set the records to be embedded

activity 3
1. use the cache reference to delete the redis cache

activity 4
1. create a query and call the pinecone for the similarity search

"""
from dataclasses import dataclass

from temporalio import activity

from providers.cache_provider.contract import CacheProvider

@dataclass
class Vector:
    file_id: int
    cache_reference_id: str
    pinecone_index: str
    


class VectorStorageActivity:
    def __init__(self, cache_provider: CacheProvider):
        self.cache_provider = cache_provider


    @activity.defn
    async def get_vectors_from_cache(self, unique_cache_id: str, file_id: int) -> Vector:
        cache = self.cache_provider.fetch(unique_cache_id)
        
        vector = Vector
        vector.file_id = file_id
        
        # we need to prepare and push the vectors to the pinecone
        
        
        
        return vector
