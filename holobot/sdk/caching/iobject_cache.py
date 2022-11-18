from typing import Any, Protocol

from .icache import ICache

class IObjectCache(ICache[Any, Any], Protocol):
    pass
