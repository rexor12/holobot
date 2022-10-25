from collections.abc import Awaitable, Callable
from itertools import islice
from typing import Generic, TypeVar

from holobot.sdk.exceptions import ArgumentError
from .iresilience_policy import IResiliencePolicy

TState = TypeVar("TState")
TResult = TypeVar("TResult")

class CombinedPolicy(Generic[TState, TResult], IResiliencePolicy[TState, TResult]):
    """A resilience policy that wraps multiple policies."""

    def __init__(self, policies: tuple[IResiliencePolicy[TState, TResult], ...]) -> None:
        super().__init__()
        if len(policies) == 0:
            raise ArgumentError("policies", "At least one policy must be specified.")

        self.__policies = policies

    async def execute(
        self,
        callback: Callable[[TState], Awaitable[TResult]],
        state: TState
    ) -> TResult:
        execute = CombinedPolicy.__wrap_policy(self.__policies[-1], callback, state)
        for policy in islice(reversed(self.__policies), 1, None):
            execute = CombinedPolicy.__wrap_execute(policy, execute, state)

        return await execute()

    @staticmethod
    def __wrap_policy(
        policy: IResiliencePolicy[TState, TResult],
        callback: Callable[[TState], Awaitable[TResult]],
        state: TState
    ) -> Callable[[], Awaitable[TResult]]:
        def wrap() -> Awaitable[TResult]:
            return policy.execute(callback, state)
        return wrap

    @staticmethod
    def __wrap_execute(
        policy: IResiliencePolicy[TState, TResult],
        execute: Callable[[], Awaitable[TResult]],
        state: TState
    ) -> Callable[[], Awaitable[TResult]]:
        def wrap() -> Awaitable[TResult]:
            return policy.execute(lambda _: execute(), state)
        return wrap
