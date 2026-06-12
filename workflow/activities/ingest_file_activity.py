import csv
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import joblib
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from temporalio import activity

from providers.cloud_storage.contract import CloudStorage
from providers.storage.contract import DataStore, Complaint, Classification

@dataclass
class FileDetails:
    """FileDetails

    Attributes:
        path: path to the CSV file in the cloud bucket
        provider: cloud storage provider name (e.g. "local", "gcs")
    """
    path: str
    provider: str # need to change it to be the cloud client

@dataclass
class _Classification:
    """_Classification

    Attributes:
        id: primary key of the classification record
        name: label assigned by the ML model (e.g. "billing", "fraud", "service")
    """
    id: int
    name: str

logging.basicConfig(level=logging.INFO)

class IngestFileActivity:
    def __init__(self, cloud_storage: CloudStorage, data_store: DataStore, mcp_url: str):
        self.cloud_storage = cloud_storage
        self.data_store = data_store
        self.mcp_url = mcp_url

    @activity.defn
    async def ingest_file_activity(self, arg: FileDetails) -> int:
        """
        Ingest file activity, we will return the file id which we got, since we can use this to find all the stored items
        :param arg: File details (path, provider)
        :return: file id
        """
        pipeline = joblib.load(Path(__file__).parents[2] / 'complaints_classifier.joblib')
        activity.logger.info(f"Ingesting file {arg.path}, provider {arg.provider},")

        # Note: we only save the file to have the id handy
        file_details = self.data_store.save_file(path=arg.path)
        # This is not a good solution
        itr = self.cloud_storage.iter_text_lines(path=arg.path)
        next(itr) # skip the header

        # doc_id, category
        for line in itr:
            activity.logger.info(f"Ingesting line {line}")
            row = next(csv.reader([line]))
            case_id, text = row[0], row[1]

            async with streamable_http_client(self.mcp_url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("pii_classify", {"text": text})
                    data = json.loads(result.content[0].text)
                    activity.logger.info(f"redacted text: {data['redacted_text']}, entities: {data['entities']}")
                    redacted_text = data['redacted_text']

            # feed into the Model for the classification
            predictions = pipeline.predict([data['redacted_text']])
            classification = await self.save_classification(name=predictions[0])


            # write into the Database
            self.data_store.save_complaint(Complaint(
                case_id=case_id,
                classification=Classification(name=classification.name, id=classification.id),
                text_redacted=redacted_text,
                embedded=False,
                file_id=file_details.id
            ))

        return  file_details.id


    async def save_classification(self, name: str) -> _Classification:
        classification = self.data_store.save_classification(name=name)
        return _Classification(
            name=classification.name,
            id=classification.id,
        )




