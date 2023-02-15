from abc import ABCMeta, abstractmethod
from collections.abc import Awaitable
from typing import Any

class IAsyncDisposable(metaclass=ABCMeta):
    async def __aenter__(self) -> Any:
        return None

    def __aexit__(self, exc_type, exc, tb) -> Awaitable[None]:
        return self._on_dispose()

    def dispose(self) -> Awaitable[None]:
        return self._on_dispose()

    @abstractmethod
    def _on_dispose(self) -> Awaitable[None]:
        raise NotImplementedError
