from collections.abc import Sequence
from typing import Any, Protocol

from holobot.sdk.diagnostics import ExecutionContextData
from .enums import LogLevel

class ILogger(Protocol):
    """Interface for a service used for writing logs.

    Where the logs appear depend on the implementation
    of the interface (such as the console or a file).
    """

    def is_log_level_enabled(self, log_level: LogLevel) -> bool:
        """Determines if the specified log level is currently enabled.

        :param log_level: The log level to test.
        :type log_level: LogLevel
        :return: True, if the specified log level is currently enabled.
        :rtype: bool
        """
        ...

    def trace(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        ...

    def debug(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        ...

    def info(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        ...

    def warning(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        ...

    def error(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        ...

    def critical(
        self,
        message: str,
        exception: Exception | None = None,
        **kwargs: Any
    ) -> None:
        ...

    def exception(self, message: str, **kwargs: Any) -> None:
        ...

    def diagnostics(self, message:str, events: Sequence[ExecutionContextData]) -> None:
        """Logs the diagnostics information of the specified events.

        :param message: The message to be logged.
        :type message: str
        :param events: A sequence of execution context data associated to each event.
        :type events: Sequence[ExecutionContextData]
        """
        ...
