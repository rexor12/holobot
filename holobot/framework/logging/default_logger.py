from collections.abc import Callable, Sequence
from typing import Any

import structlog

from holobot.sdk.diagnostics import ExecutionContextData
from holobot.sdk.logging import ILogger
from holobot.sdk.logging.enums import LogLevel
from holobot.sdk.utils import format_exception

class DefaultLogger(ILogger):
    """Default implementation of a logger."""

    def __init__(
        self,
        name: str,
        get_min_log_level: Callable[[], LogLevel]
    ) -> None:
        super().__init__()
        self.__logger = structlog.get_logger(logger_name=name)
        self.__get_min_log_level = get_min_log_level

    def is_log_level_enabled(self, log_level: LogLevel) -> bool:
        return self.__get_min_log_level() <= log_level

    def trace(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        # Forwarding to debug, because trace is not a valid structlog log level.
        DefaultLogger.__log(
            message,
            exception,
            kwargs,
            self.__logger.debug
        )

    def debug(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        DefaultLogger.__log(
            message,
            exception,
            kwargs,
            self.__logger.debug
        )

    def info(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        DefaultLogger.__log(
            message,
            exception,
            kwargs,
            self.__logger.info
        )

    def warning(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        DefaultLogger.__log(
            message,
            exception,
            kwargs,
            self.__logger.warning
        )

    def error(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        DefaultLogger.__log(
            message,
            exception,
            kwargs,
            self.__logger.error
        )

    def critical(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        DefaultLogger.__log(
            message,
            exception,
            kwargs,
            self.__logger.critical
        )

    def exception(self, message: str, **kwargs: Any) -> None:
        self.__logger.exception(message, **kwargs)

    def diagnostics(self, message:str, events: Sequence[ExecutionContextData]) -> None:
        arguments = {}
        for index, event in enumerate(events):
            arguments[f"event_{index}"] = event.event_name
            arguments[f"elapsed_{index}"] = int(event.elapsed_milliseconds)
            for extra_info_name, extra_info_value in event.extra_infos.items():
                arguments[extra_info_name] = extra_info_value

        self.__logger.debug(message, **arguments)

    @staticmethod
    def __log(
        message: str,
        exception: Exception | None,
        arguments: dict[str, Any],
        method: Callable[..., None]
    ) -> None:
        method(
            message,
            exception=format_exception(exception) if exception else None,
            exception_message=str(exception),
            **arguments
        )
