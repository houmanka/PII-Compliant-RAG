import csv
import json
import logging
from dataclasses import dataclass

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from temporalio import activity

from cloud_storage.contract import CloudStorage
from storage.contract import DataStore, Complaint


@dataclass
class FileDetails:
    path: str
    filename: str
    provider: str # need to change it to be the cloud client

@dataclass
class _Classification:
    id: int
    name: str

@dataclass
class _Complaint:
    case_id: str
    case_id: str
    redacted_text: str
    classification: _Classification


""" TODO: IMPLEMENT
    Stream file
    For each row:
        MCP pii_classify
        sanitize/redact
        classify with your ML model
        write result to the the postgres 
"""

logging.basicConfig(level=logging.INFO)

class IngestFileActivity:
    def __init__(self, cloud_storage: CloudStorage, data_store: DataStore, mcp_url: str):
        self.cloud_storage = cloud_storage
        self.data_store = data_store
        self.mcp_url = mcp_url

    @activity.defn
    async def ingest_file_activity(self, arg: FileDetails) -> str:
        activity.logger.info(f"Ingesting file {arg.path}, provider {arg.provider}, filename {arg.filename}")
        itr = self.cloud_storage.iter_text_lines(bucket=arg.path, blob_name=arg.filename)
        next(itr) # skip the header

        # doc_id, category
        for line in itr:
            activity.logger.info(f"Ingesting line {line}")
            row = next(csv.reader([line]))
            case_id, text = row[0], row[1]
            complaint = _Complaint

            complaint.case_id = case_id
            async with streamable_http_client(self.mcp_url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("pii_classify", {"text": text})
                    data = json.loads(result.content[0].text)
                    activity.logger.info(f"redacted text: {data['redacted_text']}, entities: {data['entities']}")
                    complaint.redacted_text = data['redacted_text']

            # feed into the Model for the classification











        return f"{arg.provider}:{arg.path}"




