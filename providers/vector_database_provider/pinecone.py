import time
from typing import Final

from pinecone import Pinecone, ServerlessSpec

from config import Config
from providers.vector_database_provider.contracts import VectorDatabaseProvider, VectorRecord, SimilarityResponse
from providers.vector_database_provider.registry import VectorDatabaseProviderKind, register

INDEX_NAME: Final = "pii_compliant_pipeline"
DIMENSION: Final = 384
METRIC: Final = "cosine"

class PineconeStorage(VectorDatabaseProvider):
    def __init__(self, pc: Pinecone) -> None:
        if INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=INDEX_NAME,
                vector_type="dense",
                dimension=DIMENSION,
                metric=METRIC,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                ),
                deletion_protection="disabled",
                tags={
                    "environment": "development"
                }
            )
        self.pc = pc
        index = self.ensure_index_ready()
        if index.dimension != DIMENSION or index.metric != METRIC:
            raise ValueError(
                f"Existing index '{INDEX_NAME}' has dimension {index.dimension} and metric {index.metric}, "
                f"which does not match expected dimension {DIMENSION} and metric '{METRIC}'. "
                "Please delete or rename the existing index."
            )
        self.index = pc.Index(INDEX_NAME)

    def upsert_vectors(
            self,
            vectors: list[VectorRecord],
            namespace: str = "default",
    ) -> int:

        payload = []
        for record in vectors:
            payload.append(
                {"id": record.case_id, "values": record.vector, "metadata": record.metadata}
            )

        response = self.index.upsert(vectors=payload, namespace=namespace)

        return response.upserted_count


    def query(self, vector: list[float],
            namespace: str,
            top_k: int = 3,
            filters: dict | None = None) -> list[SimilarityResponse]:
        ...

    def ensure_index_ready(self, max_wait_seconds=300):
        start_time = time.time()
        while True:
            index = self.pc.describe_index(INDEX_NAME)
            status = index.status
            if status["ready"]:
                return index
            if time.time() - start_time > max_wait_seconds:
                raise TimeoutError(f"Index {INDEX_NAME} not ready after {max_wait_seconds}s")
            time.sleep(5)



@register(VectorDatabaseProviderKind.PINECONE)
def create_vector_database(config: Config) -> PineconeStorage:
    pinecone_storage = PineconeStorage(Pinecone(api_key=config.pinecone_key.get_secret_value()))
    return pinecone_storage