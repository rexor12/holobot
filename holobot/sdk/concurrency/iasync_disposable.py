from abc import ABCMeta, abstractmethod
from typing import Any

class IAsyncDisposable(metaclass=ABCMeta):
    async def __aenter__(self) -> Any:
        return None

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._on_dispose()

    async def dispose(self) -> None:
        await self._on_dispose()

    @abstractmethod
    async def _on_dispose(self) -> None:
        raise NotImplementedError
