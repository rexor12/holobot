from __future__ import annotations
from .cancellation_token import CancellationToken
from typing import Any, Generic, TypeVar

import asyncio

TResult = TypeVar("TResult")

class CancellationPromise(Generic[TResult]):
    """Wraps a task so as to provide cancellation using a cancellation token.

    :param Generic: The type of the task's result.
    :type Generic: Generic[TResult]
    """

    def __init__(
        self,
        task: asyncio.Task[TResult],
        token: CancellationToken) -> None:
        super().__init__()
        self.__task: asyncio.Task[TResult] = task
        token.register(CancellationPromise.__cancel, self)

    def __call__(self, *args: Any, **kwds: Any) -> asyncio.Task[TResult]:
        return self.__task

    @staticmethod
    def __cancel(promise: CancellationPromise) -> None:
        promise.__task.cancel("Requested cancellation via cancellation token.") # pylint: disable=protected-access
