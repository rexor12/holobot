from collections.abc import Awaitable, Callable
from typing import Any

from holobot.sdk.threading import COMPLETED_TASK
from .iasync_disposable import IAsyncDisposable

class AsyncAnonymousDisposable(IAsyncDisposable):
    def __init__(self, on_dispose: Callable[[], Awaitable[Any]]) -> None:
        self.__on_dispose: Callable[[], Awaitable[Any]] = on_dispose
        self.__is_disposed: bool = False

    def _on_dispose(self) -> Awaitable[None]:
        if self.__is_disposed:
            return COMPLETED_TASK

        return self.__on_dispose()
