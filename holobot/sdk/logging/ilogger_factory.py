from typing import Protocol

from .ilogger import ILogger

class ILoggerFactory(Protocol):
    """Interface for a factory used for creating loggers."""

    def create(self, target_type: type) -> ILogger:
        """Creates a new logger to be used by the specified type.

        :param target_type: The type for which the logger is created.
        :type target_type: type
        :return: An instance of a logger for the specified type.
        :rtype: ILogger
        """
        ...
