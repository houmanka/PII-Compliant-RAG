from pathlib import Path
from typing import Iterator

from providers.cloud_storage.contract import CloudStorage
from providers.cloud_storage.registry import register, CloudStorageKind
from config import Config


class LocalCloudStorage(CloudStorage):
    def __init__(self, config: Config):
        # Config is accepted for factory consistency, even if LocalCloud doesn't need it yet.
        self._config = config

    _PROJECT_ROOT = Path(__file__).parents[2]

    def iter_text_lines(self, path: str) -> Iterator[str]:
        file_path = self._PROJECT_ROOT / path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found at: {file_path}")
        if not file_path.is_file():
            raise FileNotFoundError(f"Not a file: {file_path}")

        def reader() -> Iterator[str]:
            with file_path.open(mode="r", encoding="utf-8") as file:
                for line in file:
                    yield line.rstrip("\n")

        return reader()


@register(CloudStorageKind.LocalCloud)
def create_local_store(config: Config):
    return LocalCloudStorage(config)
