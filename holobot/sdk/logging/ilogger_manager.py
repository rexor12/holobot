from typing import Protocol

from .enums import LogLevel

class ILoggerManager(Protocol):
    """Interface for a service used to manipulate loggers."""

    def get_min_log_level(self) -> LogLevel:
        """Gets the currently set minimum log level.

        :return: The minimum log level.
        :rtype: LogLevel
        """
        ...

    def set_min_log_level(self, min_log_level: LogLevel) -> None:
        """Sets the current minimum log level.

        :param min_log_level: The new minimum log level.
        :type min_log_level: LogLevel
        """
        ...
