from collections.abc import Awaitable
from typing import Any, Protocol

class IAsyncDisposable(Protocol):
    async def __aenter__(self) -> Any:
        return None

    def __aexit__(self, exc_type, exc, tb) -> Awaitable[None]:
        return self._on_dispose()

    def dispose(self) -> Awaitable[None]:
        return self._on_dispose()

    def _on_dispose(self) -> Awaitable[None]:
        ...
