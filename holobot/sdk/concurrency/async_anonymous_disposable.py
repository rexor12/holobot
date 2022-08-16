from collections.abc import Callable, Coroutine
from typing import Any

from .iasync_disposable import IAsyncDisposable

class AsyncAnonymousDisposable(IAsyncDisposable):
    def __init__(self, on_dispose: Callable[[], Coroutine[Any, Any, Any]]) -> None:
        self.__on_dispose: Callable[[], Coroutine[Any, Any, Any]] = on_dispose
        self.__is_disposed: bool = False

    async def _on_dispose(self) -> None:
        if self.__is_disposed:
            return

        await self.__on_dispose()
