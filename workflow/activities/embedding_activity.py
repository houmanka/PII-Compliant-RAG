import logging

from temporalio import activity

from providers.embeddings.contracts import EmbeddingProvider
from providers.storage.contract import DataStore


logging.basicConfig(level=logging.INFO)

class EmbeddingActivity:
    def __init__(self, data_store: DataStore, embedding_provider: EmbeddingProvider):
        self.data_store = data_store
        self.embedding_provider = embedding_provider

    """
    TODO: 
    1. fetch the new records which is based on the file_id from the data store
    2. feed them through the embedding_provider
    3. push the vectors in the DragonFly and send the reference as an output
    """

    @activity.defn
    async def embedding_activity(self, file_id: int) -> str:
        return "some-key"