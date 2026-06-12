from typing import List

from sentence_transformers import SentenceTransformer

from config import Config
from providers.embeddings.contracts import EmbeddingProvider
from providers.embeddings.registry import EmbeddingProviderKind, register


class AllMiniLMEmbedding(EmbeddingProvider):
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def embed_texts(self, texts: List[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts).tolist()
        return embeddings

@register(EmbeddingProviderKind.ALL_MINILM)
def create_embedding_provider(config: Config) -> AllMiniLMEmbedding:
    model = SentenceTransformer(config.embedding_engine)
    return AllMiniLMEmbedding(model=model)