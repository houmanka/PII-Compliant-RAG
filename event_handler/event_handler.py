import uuid
from dataclasses import dataclass

from temporalio import activity

@dataclass
class FileInput:
    """FileInput

    Attributes:
        provider: cloud storage provider name (e.g. "local", "gcs")
        path: path to the file in the cloud bucket
        event_type: Pub/Sub event type that triggered this ingestion
    """
    provider: str
    path: str
    event_type: str

@activity.defn
async def ingestion_handler(arg: FileInput) -> str:
    # generate random id
    random_id = str(uuid.uuid4())

    client = activity.client()
    result = await client.execute_workflow(
        "ComplaintWorkflow",
        arg,
        id=f"ingestion-workflow-{random_id}",
        task_queue="INGESTION_QUEUE",
    )
    print(f"Result: {result}")


    return f"{arg.provider}:{arg.path}:{arg.event_type}"
