from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

from workflow.activities import ingest_file_activity
from workflow.activities.ingest_file_activity import FileDetails


@dataclass
class FileInput:
    provider: str
    path: str
    filename: str
    event_type: str

@workflow.defn(name="IngestionWorkflow")
class IngestionWorkflow:
    @workflow.run
    async def run(self, file_input: FileInput) -> str:
        return await workflow.execute_activity(
            ingest_file_activity,
            # TODO: this is the wrong provider
            FileDetails(path=file_input.path, provider=file_input.provider, filename=file_input.filename),
            start_to_close_timeout=timedelta(seconds=10),
        )