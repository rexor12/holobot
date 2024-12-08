from collections.abc import Awaitable
from typing import Any

from holobot.sdk.network import IHttpClientPool

# TODO Don't allow calls to leave the test environment.
class FakeHttpClientPool(IHttpClientPool):
    def __init__(self) -> None:
        super().__init__()

    def get(self, url: str, query_parameters: dict[str, Any] | None = None) -> Awaitable[Any]:
        raise NotImplementedError

    def get_raw(self, url: str, query_parameters: dict[str, Any] | None = None) -> Awaitable[bytes]:
        raise NotImplementedError

    def post(self, url: str, json: dict[str, Any]) -> Awaitable[Any]:
        raise NotImplementedError
