from collections.abc import Sequence
from typing import Any

import structlog

from holobot.sdk.diagnostics import ExecutionContextData
from holobot.sdk.logging import ILogger
from holobot.sdk.utils import format_exception

class DefaultLogger(ILogger):
    """Default implementation of a logger."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.__logger = structlog.get_logger(logger_name=name)

    def trace(self, message: str, **kwargs: Any) -> None:
        # Forwarding to debug, because trace is not a valid structlog log level.
        self.__logger.debug(message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self.__logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self.__logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.__logger.warning(message, **kwargs)

    def error(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        self.__logger.error(
            message,
            exception=format_exception(exception) if exception else None,
            **kwargs
        )

    def critical(self, message: str, **kwargs: Any) -> None:
        self.__logger.critical(message, **kwargs)

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
