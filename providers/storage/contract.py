from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class Classification:
    """Classification

    Attributes:
        id: primary key in the classifications table
        name: label assigned by the ML model (e.g. "billing", "fraud", "service")
    """
    id: int
    name: str

@dataclass
class File:
    """File

    Attributes:
        id: primary key in the files table
        name: filename
        path: full path to the file in the cloud bucket
    """
    id: int
    name: str
    path: str

@dataclass
class FileInput:
    """FileInput

    Attributes:
        name: filename
        path: full path to the file in the cloud bucket
    """
    name: str
    path: str

@dataclass
class Complaint:
    """Complaint

    Attributes:
        case_id: unique complaint identifier used as the idempotency key
        text_redacted: PII-redacted complaint text, the only form ever persisted
        classification: ML-assigned classification for this complaint
        file_id: foreign key referencing the source file
        embedded: whether the complaint has been pushed to the vector store
        id: primary key in the complaints table, None before first save
    """
    case_id: str
    text_redacted: str
    classification: Classification
    file_id: int
    embedded: bool = False
    id: Optional[int] = None





class DataStore(Protocol):
    def save_complaint(self, complaint: Complaint) -> Complaint: ...
    def fetch_complaint(self, complaint_id: int) -> Optional[Complaint]: ...
    def fetch_by_case_id(self, case_id: str) -> Optional[Complaint]: ...
    def fetch_unembedded(self, file_id: int) -> list[Complaint]: ...
    def mark_embedded(self, file_id: int) -> None: ...
    def save_classification(self, name: str) -> Classification: ...
    def save_file(self, path: str) -> File: ...
    def archive_file(self, file_id: int) -> None: ...
