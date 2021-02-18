from holobot.network.resilience.circuit_broken_error import CircuitBrokenError
from holobot.network.resilience.circuit_state import CircuitState
from time import time
from typing import Callable, Coroutine

import asyncio

DEFAULT_FAILURE_THRESHOLD: int = 5
DEFAULT_RECOVERY_TIMEOUT: int = 30

async def constant_break(circuit_breaker, error: Exception):
    return circuit_breaker.recovery_timeout

class AsyncCircuitBreaker:
    def __init__(self,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        recovery_timeout: int = DEFAULT_RECOVERY_TIMEOUT,
        error_evaluator = constant_break):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.error_evaluator = error_evaluator
        self.__state: CircuitState = CircuitState.CLOSED
        self.__failure_count: int = 0
        self.__close_time: int = 0

    async def __call__(self, *args, **kwds):
        return await self.call(*args, **kwds)

    @property
    def failure_threshold(self) -> int:
        return self.__failure_threshold
    
    @failure_threshold.setter
    def failure_threshold(self, value: int):
        if value <= 0:
            raise ValueError("The failure threshold must be greater than zero.")
        self.__failure_threshold = value

    @property
    def recovery_timeout(self) -> int:
        return self.__recovery_timeout
    
    @recovery_timeout.setter
    def recovery_timeout(self, value: int):
        if value <= 0:
            raise ValueError("The recovery timeout must be greater than zero.")
        self.__recovery_timeout = value
    
    @property
    def error_evaluator(self):
        return self.__error_evaluator
    
    @error_evaluator.setter
    def error_evaluator(self, corof):
        if not asyncio.iscoroutinefunction(corof):
            raise ValueError("The error evaluator be a coroutine function.")
        self.__error_evaluator = corof

    @property
    def state(self) -> CircuitState:
        if self.__state == CircuitState.OPEN and self.__close_time < time():
            return CircuitState.HALF_OPEN
        return self.__state
    
    @property
    def time_to_recover(self) -> int:
        return int(self.__close_time - time()) if self.state != CircuitState.CLOSED else 0

    async def call(self, fcoro: Callable[[], Coroutine]):
        if self.state == CircuitState.OPEN:
            raise CircuitBrokenError("The circuit is broken.")

        try:
            result = await fcoro()
        except Exception as error:
            await self.__on_failure(error)
            raise
        
        self.__on_success()
        return result
    
    async def __on_failure(self, error: Exception):
        self.__failure_count += 1
        if self.__failure_count >= self.__failure_threshold:
            recovery_timeout = await self.error_evaluator(self, error)
            self.__state = CircuitState.OPEN
            self.__close_time = time() + recovery_timeout
    
    def __on_success(self):
        self.__failure_count = 0
        self.__state == CircuitState.CLOSED