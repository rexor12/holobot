from time import time_ns
from typing import Callable, Coroutine

import asyncio

DEFAULT_RESOLUTION = 1
NO_DELAY = 0

class AsyncLoop:
    def __init__(self, method: Callable[[], Coroutine], interval: int, delay: int = NO_DELAY, resolution: int = DEFAULT_RESOLUTION):
        if not method or not isinstance(method, Callable):
            raise ValueError("The method must be a function that returns a coroutine.")
        if interval <= 0:
            raise ValueError("The interval must be greater than zero.")
        if delay < 0:
            raise ValueError("The delay must be non-negative.")
        if resolution <= 0:
            raise ValueError("The resolution must be greater than zero.")
        self.__method: Callable[[], Coroutine] = method
        self.__interval: int = int(interval * 1e9) # converting to nanoseconds
        self.__delay: int = int(delay * 1e9)
        self.__resolution: int = resolution
        self.__cancellation_requested: bool = False
    
    def __call__(self, *args, **kwds) -> Coroutine:
        return self.__loop()
    
    def cancel(self):
        self.__cancellation_requested = True

    # NOTE: For information about precision ("resolution"), refer to the following:
    # https://www.python.org/dev/peps/pep-0564/#annex-clocks-resolution-in-python
    async def __loop(self):
        elapsed: int = self.__interval - self.__delay if self.__delay != NO_DELAY else self.__interval
        while not self.__cancellation_requested:
            # If enough time has passed, it is time to execute the associated coroutine.
            if elapsed >= self.__interval:
                await self.__method()
                elapsed = 0

            # Sleep until the next cycle for checking whether cancellation has been requested.
            time = time_ns()
            await asyncio.sleep(self.__resolution)
            elapsed += time_ns() - time