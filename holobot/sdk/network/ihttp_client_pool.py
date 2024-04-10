from abc import ABCMeta, abstractmethod
from collections.abc import Awaitable
from typing import Any

# NOTE: The HTTP methods return the JSON responses.
class IHttpClientPool(metaclass=ABCMeta):
    async def close(self):
        pass

    @abstractmethod
    def get(self, url: str, query_parameters: dict[str, Any] | None = None) -> Awaitable[Any]:
        ...

    @abstractmethod
    def get_raw(self, url: str, query_parameters: dict[str, Any] | None = None) -> Awaitable[bytes]:
        ...

    @abstractmethod
    def post(self, url: str, json: dict[str, Any]) -> Awaitable[Any]:
        ...
