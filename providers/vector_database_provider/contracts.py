from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

@dataclass
class VectorRecord:
    """VectorRecord

    Attributes:
        case_id: unique complaint identifier, used as the vector id in the store
        vector: dense embedding produced by the embedding provider
        metadata: arbitrary key/value pairs stored alongside the vector (e.g. classification)
    """
    case_id: str
    vector: list[float]
    metadata: dict

@dataclass(frozen=True)
class SimilarityResponse:
    """SimilarityResponse

    Attributes:
        case_id: unique complaint identifier of the matched vector
        score: similarity score returned by the vector store (higher is more similar)
        metadata: metadata stored alongside the matched vector
    """
    case_id: str
    score: float
    metadata: dict


class VectorDatabaseProvider(ABC):

    @abstractmethod
    def upsert_vectors(
            self,
            vectors: list[VectorRecord],
            namespace: str = "default",
    ) -> int:
        """Upsert vectors and metadata for the supplied ids within a namespace.

        Args:
            vectors: Dense vectors aligned by index with ids.
            namespace: Logical partition key inside the vector store.
        """
        ...

    @abstractmethod
    def query(
            self,
            vector: list[float],
            namespace: str,
            top_k: int = 3,
            filters: dict | None = None,
    ) -> list[SimilarityResponse]:
        """Return nearest vectors as (id, score, metadata) tuples.

        Args:
            vector: Query embedding vector.
            top_k: Maximum number of results.
            namespace: Namespace to query.
            filters: Optional metadata filter expression.
        """
        ...
