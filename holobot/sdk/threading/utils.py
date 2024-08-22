import asyncio
import types
from collections.abc import Awaitable, Generator
from datetime import timedelta
from typing import Any, Generic, TypeVar

from .cancellation_promise import CancellationPromise
from .cancellation_token import CancellationToken

TResult = TypeVar("TResult")

class CompletedTask(Generic[TResult], Awaitable[TResult]):
    """A task that, when awaited, returns immediately."""

    def __init__(
        self,
        result: TResult
    ) -> None:
        super().__init__()
        self.__result = result

    def __await__(self) -> Generator[None, None, TResult]:
        yield
        return self.__result

COMPLETED_TASK: CompletedTask[None] = CompletedTask(None)

def as_task(result: TResult) -> Awaitable[TResult]:
    return CompletedTask(result)

def wait(
    timeout: timedelta | int,
    cancellation_token: CancellationToken,
    loop: asyncio.BaseEventLoop | None = None
) -> asyncio.Task[None]:
    """Asynchronously waits for the specified duration.

    :param timeout: The time to wait for, either as a timedelta or in seconds.
    :type timeout: timedelta | int
    :param cancellation_token: An optional cancellation token used for cancelling the operation.
    :type cancellation_token: CancellationToken
    :param loop: An optional asyncio event loop, defaults to None.
    :type loop: asyncio.BaseEventLoop | None, optional
    :return: An awaitable that represents the operation.
    :rtype: Awaitable[None]
    """

    active_loop = loop or asyncio.get_running_loop()
    timeout_seconds = timeout if isinstance(timeout, int) else timeout.total_seconds()
    return CancellationPromise(
        active_loop.create_task(asyncio.sleep(timeout_seconds, None)),
        cancellation_token
    )()
