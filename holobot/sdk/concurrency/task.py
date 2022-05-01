from typing import Any, Awaitable, Generator, Generic, TypeVar, Union

import asyncio

TResult = TypeVar("TResult")

class Task(Generic[TResult], Awaitable[TResult]):
    def __init__(self, result: Union[TResult, asyncio.Future[TResult]]) -> None:
        super().__init__()
        self.__result: Union[TResult, asyncio.Future[TResult]] = result

    @staticmethod
    def from_result(result: TResult) -> 'Task[TResult]':
        return Task(result)

    def __await__(self) -> Generator[Any, None, TResult]:
        yield from asyncio.sleep(0).__await__()
        if isinstance(self.__result, asyncio.Future):
            result: TResult = yield from self.__result.__await__()
            return result
        return self.__result
