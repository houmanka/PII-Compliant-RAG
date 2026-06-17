from dataclasses import dataclass
from typing import Any

from temporalio import activity

from providers.cache_provider.contract import CacheProvider
from providers.vector_database_provider.contracts import VectorDatabaseProvider, VectorRecord, SimilarityResponse


@dataclass
class VectorStorageActivityResult:
    """VectorStorageActivityResult

    Attributes:
        number_of_vectors_stored: number of vectors stored
    """
    number_of_vectors_stored: int


class VectorStorageActivity:
    def __init__(self, cache_provider: CacheProvider, vector_db_provider: VectorDatabaseProvider):
        self.cache_provider = cache_provider
        self.vector_db_provider = vector_db_provider


    @activity.defn
    async def store_vector(self, unique_cache_id: str) -> VectorStorageActivityResult:
        vector_payloads: list[VectorRecord] = self.get_vectors_from_cache(unique_cache_id)
        count = self.vector_db_provider.upsert_vectors(vector_payloads)
        if count != len(vector_payloads):
            raise RuntimeError(
                f"Pinecone upsert mismatch: expected {len(vector_payloads)}, got {count}"
            )
        return VectorStorageActivityResult(
            number_of_vectors_stored=count,
        )

    @activity.defn
    async def query_vector(self, unique_cache_id: str) -> list[SimilarityResponse]:
        vector_payloads: list[VectorRecord] = self.get_vectors_from_cache(unique_cache_id)
        response = self.vector_db_provider.query(
            vector=vector_payloads[0].vector,
            top_k=3,
             namespace="default",
            filters=None,
        )
        return response

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

