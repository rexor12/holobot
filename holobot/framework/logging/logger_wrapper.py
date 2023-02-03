from __future__ import annotations

from typing import Any

from structlog import BoundLoggerBase
from structlog.types import FilteringBoundLogger

from holobot.sdk.logging.enums import LogLevel

_LOG_LEVEL_TO_NAME = {
    LogLevel.CRITICAL: "critical",
    LogLevel.ERROR: "error",
    LogLevel.WARNING: "warning",
    LogLevel.INFORMATION: "info",
    LogLevel.DEBUG: "debug",
    LogLevel.TRACE: "debug"
}

class LoggerWrapper(BoundLoggerBase, FilteringBoundLogger):
    """A synchronous bound logger that supports filtering by log level."""

    _MIN_LOG_LEVEL: LogLevel = LogLevel.INFORMATION

    @classmethod
    def get_min_log_level(cls: type[LoggerWrapper]) -> LogLevel:
        """Gets the configured minimum log level.

        :param cls: The LoggerWrapper class or one of its inheritors.
        :type cls: type[LoggerWrapper]
        :return: The configured minimum log level.
        :rtype: LogLevel
        """

        return cls._MIN_LOG_LEVEL

    @classmethod
    def set_min_log_level(
        cls: type[LoggerWrapper],
        min_log_level: LogLevel
    ) -> None:
        """Sets the minimum log level.

        :param cls: The LoggerWrapper class or one of its inheritors.
        :type cls: type[LoggerWrapper]
        :param min_log_level: The new minimum log level.
        :type min_log_level: LogLevel
        """

        cls._MIN_LOG_LEVEL = min_log_level

    def trace(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.DEBUG, event, **kwargs)

    def debug(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.DEBUG, event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.INFORMATION, event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.WARNING, event, **kwargs)

    def warn(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.WARNING, event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.ERROR, event, **kwargs)

    def err(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.ERROR, event, **kwargs)

    def fatal(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.CRITICAL, event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> Any:
        kwargs.setdefault("exc_info", True)

        return self.__try_log(LogLevel.ERROR, event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.CRITICAL, event, **kwargs)

    def msg(self, event: str, **kwargs: Any) -> Any:
        return self.__try_log(LogLevel.INFORMATION, event, **kwargs)

    def __try_log(self, __log_level: LogLevel, __event: str, **kwargs: Any) -> Any:
        if __log_level < LoggerWrapper._MIN_LOG_LEVEL:
            return None

        return self._proxy_to_logger(_LOG_LEVEL_TO_NAME[__log_level], __event, **kwargs)
