from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar

TState = TypeVar("TState")
TResult = TypeVar("TResult")

class IResiliencePolicy(Protocol[TState, TResult]):
    """Interface for a resilience policy."""

    async def execute(
        self,
        callback: Callable[[TState], Awaitable[TResult]],
        state: TState
    ) -> TResult:
        """Invokes the specified callback and handles any errors
        according to the policy's behavior.

        :param callback: The callback to be invoked.
        :type callback: Callable[[TState], Awaitable[TResult]]
        :param state: Any object required by the callback. This is an optimization to be able to avoid closures with lambdas.
        :type state: TState
        :return: If there was no error, the value returned by the callback.
        :rtype: TResult
        """
        ...
