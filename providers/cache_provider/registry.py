from enum import Enum
from typing import Callable, Dict

from config import Config
from providers.cache_provider.contract import CacheProvider


class CacheProviderKind(str, Enum):
    REDIS = "redis"

_REGISTRY: Dict[CacheProviderKind, Callable[[Config], CacheProvider]] = {}

def register(kind: CacheProviderKind):
    def deco(factory: Callable[[Config], CacheProvider]):
        _REGISTRY[kind] = factory
        return factory
    return deco

def build_cache_provider(kind: CacheProviderKind, config: Config) -> CacheProvider:
    try:
        return _REGISTRY[kind](config)
    except KeyError:
        raise KeyError(f"Cache provider {kind} not found")