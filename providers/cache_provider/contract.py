from typing import Any
from abc import ABC, abstractmethod

class CacheProvider(ABC):
    @abstractmethod
    def create(self, key: str, value: Any) -> None: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def update(self, key: str, value: Any) -> None: ...

    @abstractmethod
    def fetch(self, key: str) -> Any: ...