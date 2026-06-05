from typing import Protocol, Iterator


class CloudStorage(Protocol):
    def iter_text_lines(self, path: str) -> Iterator[str]: ...