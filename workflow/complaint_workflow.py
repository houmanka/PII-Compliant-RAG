from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from workflow.activities.ingest_file_activity import IngestFileActivity, FileDetails


@dataclass
class FileInput:
    provider: str
    path: str
    event_type: str

@workflow.defn(name="ComplaintWorkflow")
class ComplaintWorkflow:
    @workflow.run
    async def run(self, file_input: FileInput) -> int:
        return await workflow.execute_activity(
            IngestFileActivity.ingest_file_activity,
            # TODO: this is the wrong provider
            FileDetails(path=file_input.path, provider=file_input.provider),
            start_to_close_timeout=timedelta(seconds=120),
        )