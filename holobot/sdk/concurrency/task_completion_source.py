from .task import Task
from asyncio.futures import Future
from typing import Generic, TypeVar

TResult = TypeVar("TResult")

class TaskCompletionSource(Generic[TResult]):
    def __init__(self) -> None:
        self.__future: Future[TResult] = Future()
        self.__task: Task[TResult] = Task(self.__future)
    
    def task(self) -> Task[TResult]:
        return self.__task

    def set_result(self, result: TResult) -> None:
        self.__future.set_result(result)
