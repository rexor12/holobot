from asyncio import Lock
from collections import deque
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from typing import TypeVar

from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.utils import assert_not_none
from .exceptions import RateLimitedError

TState = TypeVar("TState")
TResult = TypeVar("TResult")

class AsyncRateLimiter:
    @property
    def requests_per_interval(self) -> int:
        return self.__requests_per_interval

    @property
    def interval(self) -> timedelta:
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
        self.__lock = Lock()
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
                erase_before = datetime.now(timezone.utc) - self.__interval
                while (
                    self.__request_timestamps
                    and self.__request_timestamps[0] < erase_before
                ):
                    self.__request_timestamps.popleft()
            if len(self.__request_timestamps) >= self.__requests_per_interval:
                raise RateLimitedError(
                    self.__request_timestamps[0] + self.__interval - datetime.now(timezone.utc)
                )

            self.__request_timestamps.append(datetime.now(timezone.utc))

        return await callback(state)
