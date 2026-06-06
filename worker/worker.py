import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker
from providers.cloud_storage.registry import build_cloud_storage, CloudStorageKind
from config import Config, get_config
from event_handler.event_handler import ingestion_handler
from providers.embeddings.registry import build_embedding_provider, EmbeddingProviderKind
from providers.storage.registry import build_data_store, DataStorageKind
from workflow.activities.embedding_activity import EmbeddingActivity
from workflow.activities.ingest_file_activity import IngestFileActivity
from workflow.complaint_workflow import ComplaintWorkflow


async def main():
    connect_config = ClientConfig.load_client_connect_config()
    connect_config.setdefault("target_host", "localhost:7233")

    conf = Config()

    # define all the providers
    cloud_storage_provider = build_cloud_storage(kind=CloudStorageKind.LocalCloud ,config=conf)
    data_storage_provider = build_data_store(kind=DataStorageKind.POSTGRES ,config=conf)
    embedding_provider = build_embedding_provider(kind=EmbeddingProviderKind.ALL_MINILM, config=conf)

    # Activity class
    ingestion_activity_obj = IngestFileActivity(cloud_storage=cloud_storage_provider, data_store=data_storage_provider, mcp_url=get_config().mcp_path)
    embedding_activity_obj = EmbeddingActivity(data_store=data_storage_provider, embedding_provider=embedding_provider)


    client = await Client.connect(**connect_config)
    worker = Worker(
        client,
        task_queue="INGESTION_QUEUE",
        activities=[ingestion_handler,
                    ingestion_activity_obj.ingest_file_activity,
                    embedding_activity_obj.embedding_activity],
        workflows=[ComplaintWorkflow],
        activity_executor=ThreadPoolExecutor(5),
    )
    print("worker running...", end="", flush=True)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())