import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker
from cloud_storage.registry import build_cloud_storage, CloudStorageKind
from config import Config, get_config
from event_handler.event_handler import ingestion_handler
from storage.registry import build_data_store, DataStorageKind
from workflow.activities.ingest_file_activity import IngestFileActivity
from workflow.complaint_workflow import ComplaintWorkflow


async def main():
    connect_config = ClientConfig.load_client_connect_config()
    connect_config.setdefault("target_host", "localhost:7233")

    conf = Config()

    # create cloud storage client
    cloud_storage = build_cloud_storage(kind=CloudStorageKind.LocalCloud ,config=conf)

    data_storage = build_data_store(kind=DataStorageKind.POSTGRES ,config=conf)

    ingestion_activity = IngestFileActivity(cloud_storage=cloud_storage, data_store=data_storage, mcp_url=get_config().mcp_path)


    client = await Client.connect(**connect_config)
    worker = Worker(
        client,
        task_queue="INGESTION_QUEUE",
        activities=[ingestion_handler, ingestion_activity.ingest_file_activity],
        workflows=[ComplaintWorkflow],
        activity_executor=ThreadPoolExecutor(5),
    )
    print("worker running...", end="", flush=True)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())