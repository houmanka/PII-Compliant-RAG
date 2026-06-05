from enum import Enum
from typing import Callable, Dict, Protocol, Any

from pydantic import SecretStr

class DataStorageKind(str, Enum):
    POSTGRES = "postgres"

_REGISTRY: Dict[DataStorageKind, Callable] = {}

class HasDatabaseURL(Protocol):
    database_url: SecretStr

def register(kind: DataStorageKind):
    def deco(factory: Callable):
        _REGISTRY[kind] = factory
        return factory
    return deco

def build_data_store(kind: DataStorageKind, config: HasDatabaseURL) -> ValueError | Any:
    try:
        return _REGISTRY[kind](config)
    except KeyError:
        raise ValueError(f"Data storage kind {kind} not supported")