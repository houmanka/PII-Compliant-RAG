from unittest.mock import create_autospec

import pytest

from cloud_storage.contract import CloudStorage
from storage.contract import DataStore
from workflow.activities.ingest_file_activity import FileDetails, IngestFileActivity


def make_activity(lines: list[str]) -> IngestFileActivity:
    cloud_storage = create_autospec(CloudStorage)
    cloud_storage.iter_text_lines.return_value = iter(["case_id,text"] + lines)
    data_store = create_autospec(DataStore)
    return IngestFileActivity(
        cloud_storage=cloud_storage,
        data_store=data_store,
        mcp_url="http://localhost:8090/mcp",
    )


@pytest.mark.anyio
async def test_ingest_file_activity_no_pii():
    activity = make_activity(["CASE-001,The service was slow yesterday"])
    result = await activity.ingest_file_activity(FileDetails(path="my-bucket", filename="complaints.csv", provider="gcs"))
    assert result == "gcs:my-bucket"


@pytest.mark.anyio
async def test_ingest_file_activity_email_pii():
    activity = make_activity(["CASE-002,Please contact me at john.doe@example.com"])
    result = await activity.ingest_file_activity(FileDetails(path="my-bucket", filename="complaints.csv", provider="gcs"))
    assert result == "gcs:my-bucket"


@pytest.mark.anyio
async def test_ingest_file_activity_phone_pii():
    activity = make_activity(["CASE-003,Call me on 415-555-0198 to resolve this"])
    result = await activity.ingest_file_activity(FileDetails(path="my-bucket", filename="complaints.csv", provider="gcs"))
    assert result == "gcs:my-bucket"


@pytest.mark.anyio
async def test_ingest_file_activity_name_pii():
    activity = make_activity(["CASE-004,My name is John Smith and my account is overcharged"])
    result = await activity.ingest_file_activity(FileDetails(path="my-bucket", filename="complaints.csv", provider="gcs"))
    assert result == "gcs:my-bucket"


@pytest.mark.anyio
async def test_ingest_file_activity_multiple_rows():
    activity = make_activity([
        "CASE-005,The service was down",
        "CASE-006,Contact me at jane@example.com or 212-555-0100",
    ])
    result = await activity.ingest_file_activity(FileDetails(path="my-bucket", filename="complaints.csv", provider="gcs"))
    assert result == "gcs:my-bucket"
