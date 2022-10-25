from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Generic, TypeVar

from .async_circuit_breaker_policy import (
    DEFAULT_FAILURE_THRESHOLD as DEFAULT_CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    DEFAULT_RECOVERY_TIMEOUT as DEFAULT_CIRCUIT_BREAKER_RECOVERY_TIMEOUT, AsyncCircuitBreakerPolicy,
    constant_break
)
from .async_rate_limit_policy import AsyncRateLimitPolicy
from .async_retry_policy import AsyncRetryPolicy
from .combined_policy import CombinedPolicy
from .iresilience_policy import IResiliencePolicy

TState = TypeVar("TState")
TResult = TypeVar("TResult")

class CombinedPolicyBuilder(Generic[TState, TResult]):
    """A builder for combining resilience policies.

    The order in which the policies are configured
    is the order in which they are executed.
    """

    def __init__(self) -> None:
        self.__policies = list[IResiliencePolicy[TState, TResult]]()

    def circuit_breaker(
        self,
        failure_threshold: int = DEFAULT_CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        recovery_timeout: int = DEFAULT_CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
        error_evaluator: Callable[[AsyncCircuitBreakerPolicy[TState, TResult], Exception], Awaitable[int]] = constant_break
    ) -> CombinedPolicyBuilder[TState, TResult]:
        """Configures a circuit breaker policy.

        :param failure_threshold: The number of consecutive failures after which the circuit breaks, defaults to DEFAULT_CIRCUIT_BREAKER_FAILURE_THRESHOLD
        :type failure_threshold: int, optional
        :param recovery_timeout: The duration to wait before the circuit is restored, defaults to DEFAULT_CIRCUIT_BREAKER_RECOVERY_TIMEOUT
        :type recovery_timeout: int, optional
        :param error_evaluator: A function invoked when the circuit breaks, defaults to constant_break
        :type error_evaluator: Callable[[AsyncCircuitBreakerPolicy[TState, TResult], Exception], Awaitable[int]], optional
        :return: The same instance of policy builder.
        :rtype: CombinedPolicyBuilder[TState, TResult]
        """

        self.__policies.append(AsyncCircuitBreakerPolicy[TState, TResult](
            failure_threshold,
            recovery_timeout,
            error_evaluator
        ))
        return self

    def rate_limiter(
        self,
        requests_per_interval: int,
        interval: timedelta | int
    ) -> CombinedPolicyBuilder[TState, TResult]:
        """Configures a rate limit policy.

        :param requests_per_interval: The number of requests allowed in an interval.
        :type requests_per_interval: int
        :param interval: The length of the sliding window.
        :type interval: timedelta | int
        :return: The same instance of policy builder.
        :rtype: CombinedPolicyBuilder[TState, TResult]
        """

        self.__policies.append(AsyncRateLimitPolicy[TState, TResult](
            requests_per_interval,
            interval if isinstance(interval, timedelta) else timedelta(seconds=interval)
        ))
        return self

    def retry(
        self,
        max_attempt_count: int,
        retry_after: Callable[[AsyncRetryPolicy[TState, TResult], int, Exception], timedelta] | timedelta | int,
        ignored_exceptions: type[Exception] | tuple[type[Exception], ...] | None = None
    ) -> CombinedPolicyBuilder[TState, TResult]:
        """Configures a retry policy.

        :param max_attempt_count: The maximum number of attempts before propagating the error.
        :type max_attempt_count: int
        :param retry_after: The duration to wait between each attempt.
        :type retry_after: Callable[[AsyncRetryPolicy[TState, TResult], int, Exception], timedelta] | timedelta | int
        :param ignored_exceptions: The exceptions to be handled. Any non-specified exception is immediately propagated without retries. If not specified, all exceptions are handled, defaults to None
        :type ignored_exceptions: type[Exception] | tuple[type[Exception], ...] | None, optional
        :return: The same instance of policy builder.
        :rtype: CombinedPolicyBuilder[TState, TResult]
        """

        self.__policies.append(AsyncRetryPolicy[TState, TResult](
            max_attempt_count,
            (
                retry_after
                if isinstance(retry_after, (timedelta, Callable))
                else timedelta(seconds=retry_after)
            ),
            ignored_exceptions
        ))
        return self

    def build(self) -> IResiliencePolicy[TState, TResult]:
        """Builds the combined resilience policy.

        :return: The new instance of combined resilience policy.
        :rtype: IResiliencePolicy[TState, TResult]
        """

        return CombinedPolicy[TState, TResult](tuple(self.__policies))
