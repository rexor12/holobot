from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from time import time
from typing import Generic, TypeVar

from .exceptions.circuit_broken_error import CircuitBrokenError
from .iresilience_policy import IResiliencePolicy
from .models.circuit_state import CircuitState

TState = TypeVar("TState")
TResult = TypeVar("TResult")

DEFAULT_FAILURE_THRESHOLD: int = 5
DEFAULT_RECOVERY_TIMEOUT: int = 30

async def constant_break(
    circuit_breaker: AsyncCircuitBreakerPolicy,
    error: Exception
) -> int:
    """Default implementation of an error handler.

    It always returns the configured recovery time.

    :param circuit_breaker: The circuit breaker that failed.
    :type circuit_breaker: AsyncCircuitBreakerPolicy
    :param error: The exception that caused the failure.
    :type error: Exception
    :return: The configured recovery time of the circuit breaker.
    :rtype: int
    """

    return circuit_breaker.recovery_timeout

class AsyncCircuitBreakerPolicy(Generic[TState, TResult], IResiliencePolicy[TState, TResult]):
    """A resilience policy for preventing spam on failure."""

    @property
    def failure_threshold(self) -> int:
        """The number of consecutive failures after which the circuit breaks."""

        return self.__failure_threshold

    @failure_threshold.setter
    def failure_threshold(self, value: int):
        if value <= 0:
            raise ValueError("The failure threshold must be greater than zero.")
        self.__failure_threshold = value

    @property
    def recovery_timeout(self) -> int:
        """The duration to wait before the circuit is restored."""

        return self.__recovery_timeout

    @recovery_timeout.setter
    def recovery_timeout(self, value: int):
        if value <= 0:
            raise ValueError("The recovery timeout must be greater than zero.")
        self.__recovery_timeout = value

    @property
    def error_evaluator(self) -> Callable[[AsyncCircuitBreakerPolicy, Exception], Awaitable[int]]:
        """A function invoked when the circuit breaks.

        This function may also be used to override the default recovery time.
        """

        return self.__error_evaluator

    @error_evaluator.setter
    def error_evaluator(
        self,
        value: Callable[[AsyncCircuitBreakerPolicy, Exception], Awaitable[int]]
    ) -> None:
        self.__error_evaluator = value

    @property
    def state(self) -> CircuitState:
        """The current state of the circuit."""

        if self.__state is CircuitState.OPEN and self.__close_time < time():
            return CircuitState.HALF_OPEN
        return self.__state

    @property
    def time_to_recover(self) -> int:
        """The time (in seconds) left until the circuit is restored."""

        return (
            int(self.__close_time - time())
            if self.state is not CircuitState.CLOSED
            else 0
        )

    def __init__(
        self,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        recovery_timeout: int = DEFAULT_RECOVERY_TIMEOUT,
        error_evaluator: Callable[[AsyncCircuitBreakerPolicy, Exception], Awaitable[int]] = constant_break
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.error_evaluator = error_evaluator
        self.__state: CircuitState = CircuitState.CLOSED
        self.__failure_count: int = 0
        self.__close_time: int = 0
        self.__lock = asyncio.Lock()

    async def __call__(
        self,
        callback: Callable[[TState], Awaitable[TResult]],
        state: TState
    ) -> TResult:
        return await self.execute(callback, state)

    async def execute(
        self,
        callback: Callable[[TState], Awaitable[TResult]],
        state: TState
    ) -> TResult:
        # Double checking outside the lock as a fast fail optimization.
        if self.state is CircuitState.OPEN:
            raise CircuitBrokenError("The circuit is broken.")

        async with self.__lock:
            if self.state is CircuitState.OPEN:
                raise CircuitBrokenError("The circuit is broken.")

            try:
                result = await callback(state)
            except Exception as error:
                await self.__on_failure(error)
                raise

            self.__on_success()
            return result

    async def __on_failure(self, error: Exception):
        self.__failure_count += 1
        if self.__failure_count >= self.__failure_threshold:
            # TODO Support datetime and int as well (from the Retry-After HTTP header).
            recovery_timeout = await self.error_evaluator(self, error)
            self.__state = CircuitState.OPEN
            self.__close_time = int(time() + recovery_timeout)

    def __on_success(self):
        self.__failure_count = 0
        self.__state = CircuitState.CLOSED
