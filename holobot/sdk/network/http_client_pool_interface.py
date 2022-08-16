from abc import ABCMeta, abstractmethod
from typing import Any

# NOTE: The HTTP methods return the JSON responses.
class HttpClientPoolInterface(metaclass=ABCMeta):
    async def close(self):
        pass

    @abstractmethod
    async def get(self, url: str, query_parameters: dict[str, Any] | None = None) -> Any:
        ...

    @abstractmethod
    async def post(self, url: str, json: dict[str, Any]) -> Any:
        ...
