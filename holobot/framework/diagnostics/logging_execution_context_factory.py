from typing import Any

from .execution_context_wrapper import ExecutionContextWrapper
from holobot.sdk.diagnostics import (
    ExecutionContext, IExecutionContext, IExecutionContextFactory,
    Stopwatch
)
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

@injectable(IExecutionContextFactory)
class LoggingExecutionContextFactory(IExecutionContextFactory):
    def __init__(
        self,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(LoggingExecutionContextFactory)

    def create(
        self,
        message: str,
        event_name: str,
        extra_info: dict[str, Any] | None = None
    ) -> IExecutionContext:
        if extra_info is None:
            extra_info = {}

        context = ExecutionContext()
        stopwatch = context.start(event_name, extra_info)
        return ExecutionContextWrapper(
            context,
            lambda: self.__dispose_context(context, stopwatch, message)
        )

    def __dispose_context(
        self,
        context: ExecutionContext,
        stopwatch: Stopwatch,
        message: str
    ) -> None:
        stopwatch.dispose()
        self.__logger.diagnostics(message, context.collect())
