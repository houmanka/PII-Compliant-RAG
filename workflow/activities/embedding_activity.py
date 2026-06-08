import logging
import uuid
from dataclasses import dataclass

from temporalio import activity

from providers.cache_provider.contract import CacheProvider
from providers.embeddings.contracts import EmbeddingProvider
from providers.storage.contract import DataStore


logging.basicConfig(level=logging.INFO)

@dataclass
class EmbeddingActivityResult:
    file_id: int
    cache_id: str

class EmbeddingActivity:
    def __init__(self, data_store: DataStore, embedding_provider: EmbeddingProvider, cache_provider: CacheProvider):
        self.data_store = data_store
        self.embedding_provider = embedding_provider
        self.cache_provider = cache_provider

    @activity.defn
    async def embedding_activity(self, file_id: int) -> EmbeddingActivityResult:
        compliant_list = self.data_store.fetch_unembedded(file_id)
        unique_cache_key = await self.get_a_unique_cache_key(file_id)

        dragonfly_key = f"vectors:{unique_cache_key}"
        vectored_ready = [complaint.text_redacted for complaint in compliant_list]
        embedded_text = self.embedding_provider.embed_texts(vectored_ready)

        self.cache_provider.create(dragonfly_key, embedded_text)
        return EmbeddingActivityResult(file_id=file_id, cache_id=unique_cache_key)

    async def get_a_unique_cache_key(self, file_id: int) -> str:
        session_id = str(uuid.uuid4())
        if self.cache_provider.exists(session_id):
            return await self.get_a_unique_cache_key(file_id)
        return session_id