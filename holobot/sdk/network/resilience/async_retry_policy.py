from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Generic, TypeVar

from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.utils import assert_not_none
from .iresilience_policy import IResiliencePolicy

TState = TypeVar("TState")
TResult = TypeVar("TResult")

class AsyncRetryPolicy(Generic[TState, TResult], IResiliencePolicy[TState, TResult]):
    """A resilience policy for retrying an operation on errors."""

    __ZERO_TIMEDELTA = timedelta()

    @property
    def max_attempt_count(self) -> int:
        """The maximum number of attempts before propagating the error."""

        return self.__max_attempt_count

    @property
    def retry_after(
        self
    ) -> Callable[[AsyncRetryPolicy[TState, TResult], int, Exception], timedelta] | timedelta:
        """The duration to wait between each attempt."""

        return self.__retry_after

    @property
    def ignored_exceptions(self) -> type[Exception] | tuple[type[Exception], ...] | None:
        """The exceptions to be handled.

        Any non-specified exception is immediately propagated without retries.
        If not specified, all exceptions are handled."""

        return self.__ignored_exceptions

    def __init__(
        self,
        max_attempt_count: int,
        retry_after: Callable[['AsyncRetryPolicy', int, Exception], timedelta] | timedelta,
        ignored_exceptions: type[Exception] | tuple[type[Exception], ...] | None = None
    ) -> None:
        if max_attempt_count < 1:
            raise ArgumentOutOfRangeError("max_attempt_count", "1", "infinite")
        if isinstance(retry_after, timedelta) and retry_after < timedelta():
            raise ArgumentOutOfRangeError("retry_after", "0", "infinite")

        self.__max_attempt_count = max_attempt_count
        self.__retry_after = retry_after
        self.__ignored_exceptions = ignored_exceptions
        self.__lock = asyncio.Lock()

    def __call__(
        self,
        callback: Callable[[TState], Awaitable[TResult]],
        state: TState
    ) -> Awaitable[TResult]:
        return self.execute(callback, state)

    async def execute(
        self,
        callback: Callable[[TState], Awaitable[TResult]],
        state: TState
    ) -> TResult:
        assert_not_none(callback, "callback")

        async with self.__lock:
            for index in range(self.max_attempt_count):
                try:
                    return await callback(state)
                except Exception as error:
                    if self.__should_raise(index, error):
                        raise

                    retry_after = (
                        self.retry_after
                        if isinstance(self.retry_after, timedelta)
                        else self.retry_after(self, index, error)
                    )
                    if retry_after > AsyncRetryPolicy.__ZERO_TIMEDELTA:
                        await asyncio.sleep(retry_after.total_seconds())

        # We must never reach this point, because of one of the following:
        # a) the callback was successful,
        # b) we reached the max attempts,
        # c) we got an unhandled exception.
        assert False

    def __should_raise(
        self,
        attempt_index: int,
        exception: Exception
    ) -> bool:
        # Reached max attempts, raise.
        if attempt_index >= self.max_attempt_count - 1:
            return True

        # All exceptions are swallowed.
        if not self.ignored_exceptions:
            return False

        if isinstance(self.ignored_exceptions, type):
            # If not a handled exception, raise.
            return not isinstance(exception, self.ignored_exceptions)

        for exception_type in self.ignored_exceptions:
            # Handled exception, swallow.
            if isinstance(exception, exception_type):
                return False

        # Not a handled exception, raise.
        return True
