from holobot.sdk import Maybe
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.utils import assert_not_none, assert_range
from typing import Generic, List, TypeVar

import asyncio, sys

T = TypeVar("T")

INFINITE_CAPACITY = -1
LAST_POSITION = -1

class AsyncProducerConsumerQueue(Generic[T]):
    _EMPTY_MAYBE: Maybe[T] = Maybe()

    def __init__(self, capacity: int = INFINITE_CAPACITY) -> None:
        if capacity != INFINITE_CAPACITY:
            assert_range(capacity, 1, sys.maxsize, "capacity")
        self.__capacity: int = capacity
        self.__is_complete: bool = False
        self.__queue: List[T] = []
        self.__lock: asyncio.Lock = asyncio.Lock()

    async def enqueue(self, item: T, position: int = LAST_POSITION) -> None:
        assert_not_none(item, "item")
        if position != LAST_POSITION:
            assert_range(position, 0, len(self.__queue), "position")

        async with self.__lock:
            self.__throw_if_completed()
            if self.__capacity != INFINITE_CAPACITY and len(self.__queue) + 1 > self.__capacity:
                raise InvalidOperationError("The queue is full.")
            if position == LAST_POSITION:
                self.__queue.append(item)
            else: self.__queue.insert(position, item)

    async def try_dequeue(self) -> Maybe[T]:
        async with self.__lock:
            self.__throw_if_completed()
            return Maybe(self.__queue.pop(0)) if len(self.__queue) > 0 else AsyncProducerConsumerQueue._EMPTY_MAYBE

    async def peek(self, selector: slice) -> List[T]:
        assert_not_none(selector, "selector")

        async with self.__lock:
            return self.__queue[selector]

    async def complete(self) -> None:
        async with self.__lock:
            self.__is_complete = True

    async def clear(self) -> None:
        async with self.__lock:
            self.__queue.clear()

    def __len__(self) -> int:
        return len(self.__queue)

    def __throw_if_completed(self) -> None:
        if self.__is_complete:
            raise InvalidOperationError("The queue has been completed.")
