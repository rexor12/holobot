from typing import Optional

import structlog

from holobot.sdk.logging import ILogger
from holobot.sdk.utils import format_exception

class DefaultLogger(ILogger):
    """Default implementation of a logger."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.__logger = structlog.get_logger(logger_name=name)

    def trace(self, message: str, **kwargs) -> None:
        self.__logger.trace(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        self.__logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self.__logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self.__logger.warning(message, **kwargs)

    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs
    ) -> None:
        self.__logger.error(
            message,
            exception=format_exception(exception) if exception else None,
            **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self.__logger.critical(message, **kwargs)

    def exception(self, message: str) -> None:
        self.__logger.exception(message)
