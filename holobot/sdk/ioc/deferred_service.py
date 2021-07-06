from .tservice import TService
from asyncio import Lock
from typing import Callable, Generic, Optional

class DeferredService(Generic[TService]):
    """A wrapper around the service that resolves the instance lazily.

    This class wraps a function used for resolving an instance of a service.
    It is useful when you don't immediately want to use a service in the 
    __init__ function (where the "constructor injection" happens).
    The real advantage is with this deferred resolution, cycles in the 
    dependency graph are supported.
    """

    def __init__(self, resolver: Callable[[], TService]) -> None:
        self.__resolver: Callable[[], TService] = resolver
        self.__lock: Lock = Lock()
        self.__service: Optional[TService] = None
    
    async def resolve(self) -> TService:
        """Resolves the instance of the wrapped service.

        If the instance is already resolved, it's returned immediately
        instead of creating a new instance.

        Returns
        -------
        TService
            The resolved instance of the wrapped service.
        """

        if self.__service is not None:
            return self.__service

        async with self.__lock:
            if self.__service is not None:
                # This can happen due to asynchronity; it's a false positive syntax error.
                return self.__service
            
            print(f"TService = {TService}")
            self.__service = self.__resolver()
            return self.__service
