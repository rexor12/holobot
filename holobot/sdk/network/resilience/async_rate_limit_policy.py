import asyncio
from collections import deque
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import Generic, TypeVar

from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.utils import assert_not_none, utcnow
from .exceptions import RateLimitedError
from .iresilience_policy import IResiliencePolicy

TState = TypeVar("TState")
TResult = TypeVar("TResult")

class AsyncRateLimitPolicy(Generic[TState, TResult], IResiliencePolicy[TState, TResult]):
    """A resilience policy for limiting the rate at which operations are performed."""

    @property
    def requests_per_interval(self) -> int:
        """The number of requests allowed in an interval.

        Any excess requests result in an exception.
        """

        return self.__requests_per_interval

    @property
    def interval(self) -> timedelta:
        """The length of the sliding window."""

        return self.__interval

    def __init__(
        self,
        requests_per_interval: int,
        interval: timedelta
    ) -> None:
        if requests_per_interval < 1:
            raise ArgumentOutOfRangeError("requests_per_interval", "1", "infinite")
        if interval < timedelta():
            raise ArgumentOutOfRangeError("interval", "0", "infinite")

        self.__requests_per_interval = requests_per_interval
        self.__interval = interval
        self.__lock = asyncio.Lock()
        self.__request_timestamps = deque[datetime](maxlen=requests_per_interval)

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
            if self.__request_timestamps:
                erase_before = utcnow() - self.__interval
                while (
                    self.__request_timestamps
                    and self.__request_timestamps[0] < erase_before
                ):
                    self.__request_timestamps.popleft()
            if len(self.__request_timestamps) >= self.__requests_per_interval:
                raise RateLimitedError(
                    self.__request_timestamps[0] + self.__interval - utcnow()
                )

            self.__request_timestamps.append(utcnow())

        return await callback(state)
