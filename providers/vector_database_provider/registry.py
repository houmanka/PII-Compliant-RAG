from enum import Enum
from typing import Callable, Dict

from config import Config
from providers.vector_database_provider.contracts import VectorDatabaseProvider


class VectorDatabaseProviderKind(str, Enum):
    PINECONE = "pinecone"

_REGISTRY: Dict[VectorDatabaseProviderKind, Callable[[Config], VectorDatabaseProvider]] = {}

def register(kind: VectorDatabaseProviderKind):
    def deco(factory: Callable[[Config], VectorDatabaseProvider]):
        _REGISTRY[kind] = factory
        return factory
    return deco

def build_vector_db_provider(kind: VectorDatabaseProviderKind, config: Config) -> VectorDatabaseProvider:
    try:
        return _REGISTRY[kind](config)
    except KeyError:
        raise KeyError(f"Unknown Vector Database kind {kind}")