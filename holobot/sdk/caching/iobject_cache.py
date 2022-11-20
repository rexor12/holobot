from typing import Any, Protocol

from .icache import ICache

class IObjectCache(ICache[Any, Any], Protocol):
    """Interface for a cache that can store any type of item."""
