from typing import Any, Awaitable, Generator, Generic, TypeVar

import asyncio

TResult = TypeVar("TResult")

class Task(Generic[TResult], Awaitable[TResult]):
    def __init__(self, result: TResult) -> None:
        super().__init__()
        self.__result: TResult = result

    @staticmethod
    def from_result(result: TResult) -> 'Task[TResult]':
        return Task(result)

    def __await__(self) -> Generator[Any, None, TResult]:
        yield from asyncio.sleep(0).__await__()
        return self.__result
