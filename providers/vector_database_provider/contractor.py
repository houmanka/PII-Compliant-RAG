from dataclasses import dataclass
from typing import Protocol

@dataclass
class VectorRecord:
    case_id: str
    vector: list[float]

@dataclass(frozen=True)
class SimilarityResponse:
    case_id: str
    score: float


class VectorDatabaseProvider(Protocol):
    def upsert(self, vectors: list[VectorRecord]) -> int:
        ...
    def query(self, vector: list[float], top_k: int = 3) -> list[SimilarityResponse]:
        ...