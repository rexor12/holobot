from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional

# NOTE: The HTTP methods return the JSON responses.
class HttpClientPoolInterface(metaclass=ABCMeta):
    async def close(self):
        pass

    @abstractmethod
    async def get(self, url: str, query_parameters: Optional[Dict[str, Any]] = None) -> Any:
        ...

    @abstractmethod
    async def post(self, url: str, json: Dict[str, Any]) -> Any:
        ...
