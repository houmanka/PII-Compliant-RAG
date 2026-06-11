from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from workflow.activities.ingest_file_activity import IngestFileActivity, FileDetails
    from workflow.activities.embedding_activity import EmbeddingActivity, EmbeddingActivityResult


@dataclass
class FileInput:
    """FileInput

    Attributes:
        provider: cloud storage provider name (e.g. "local", "gcs")
        path: path to the file in the cloud bucket
        event_type: Pub/Sub event type that triggered this workflow
    """
    provider: str
    path: str
    event_type: str

@workflow.defn(name="ComplaintWorkflow")
class ComplaintWorkflow:
    @workflow.run
    async def run(self, file_input: FileInput) -> bool:
        file_id = await workflow.execute_activity(
            IngestFileActivity.ingest_file_activity,
            # TODO: this is the wrong provider
            FileDetails(path=file_input.path, provider=file_input.provider),
            start_to_close_timeout=timedelta(seconds=120),
        )

        embedding_result: EmbeddingActivityResult = await workflow.execute_activity(
            EmbeddingActivity.embedding_activity,
            file_id,
            start_to_close_timeout=timedelta(seconds=120),
        )

        return embedding_result