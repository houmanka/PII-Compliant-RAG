"""
activity 1 (DONE)
1. based on the reference of the cache, return the vectors
2. set them up based on what Pinecone needs
3. Push your vectors to the pinecone storage
4. return the number_of_vectors_stored: int, success: bool

activity 2 (TODO)
1. use the file_id and update the database to set the records to be embedded

activity 3 (TODO)
1. use the cache reference to delete the redis cache

activity 4 (TODO)
1. create a query and call the pinecone for the similarity search

"""
from dataclasses import dataclass

from temporalio import activity

from providers.cache_provider.contract import CacheProvider
from providers.vector_database_provider.contracts import VectorDatabaseProvider, VectorRecord

@dataclass
class VectorStorageActivityResult:
    """VectorStorageActivityResult

    Attributes:
        number_of_vectors_stored: number of vectors stored
        success: if successful
    """
    number_of_vectors_stored: int
    success: bool


class VectorStorageActivity:
    def __init__(self, cache_provider: CacheProvider, vector_db_provider: VectorDatabaseProvider):
        self.cache_provider = cache_provider
        self.vector_db_provider = vector_db_provider


    @activity.defn
    async def store_vector(self, unique_cache_id: str) -> VectorStorageActivityResult:
        vector_payloads: list[VectorRecord] = self.get_vectors_from_cache(unique_cache_id)
        count = self.vector_db_provider.upsert_vectors(vector_payloads)
        if count == len(vector_payloads):
            return VectorStorageActivityResult(
                number_of_vectors_stored=count,
                success=True,
            )
        return VectorStorageActivityResult(
            number_of_vectors_stored=count,
            success=False,
        )


    def get_vectors_from_cache(self, unique_cache_id: str) -> list[VectorRecord]:
        # this is list of tuples from (case_id, vector, classification_name) saved in our cache
        records: list[tuple[str, list[float], str]] = self.cache_provider.fetch(unique_cache_id)
        v = []
        for case_id, vector, classification_name in records:
            v.append(VectorRecord(
                vector=vector,
                case_id=case_id,
                metadata={"classification": classification_name},
            ))

        return v

