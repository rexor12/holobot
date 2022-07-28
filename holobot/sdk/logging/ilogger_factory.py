from typing import Any, Protocol, Type

from .ilogger import ILogger

class ILoggerFactory(Protocol):
    """Interface for a factory used for creating loggers."""

    def create(self, target_type: Type[Any]) -> ILogger:
        """Creates a new logger to be used by the specified type.

        :param target_type: The type for which the logger is created.
        :type target_type: Type[Any]
        :return: An instance of a logger for the specified type.
        :rtype: ILogger
        """
        ...
