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
    client = activity.client()
    handle = await client.start_workflow(
        "ComplaintWorkflow",
        arg,
        id=f"complaint-workflow-{arg.path}",
        task_queue="INGESTION_QUEUE",
    )

    return handle.id
