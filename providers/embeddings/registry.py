from enum import Enum
from typing import Callable

from config import Config
from providers.embeddings.contracts import EmbeddingProvider


class EmbeddingProviderKind(str, Enum):
    ALL_MINILM = "all-mini-lm"


_REGISTRY: dict[EmbeddingProviderKind, Callable[[Config], EmbeddingProvider]] = {}

def register(kind: EmbeddingProviderKind):
    def deco(factory: Callable):
        _REGISTRY[kind] = factory
        return factory
    return deco

def build_embedding_provider(kind: EmbeddingProviderKind, config: Config):
    """Build an embeddings provider from registry.

        Args:
            kind: Embeddings provider enum key.
            config: Config
    """
    try:
        return _REGISTRY[kind](config)
    except KeyError:
        raise ValueError(f"Unknown embeddings provider kind: {kind}")