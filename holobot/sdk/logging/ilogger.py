from typing import Any, Optional, Protocol

class ILogger(Protocol):
    """Interface for a service used for writing logs.

    Where the logs appear depend on the implementation
    of the interface (such as the console or a file).
    """

    def trace(self, message: str, **kwargs: Any) -> None:
        ...

    def debug(self, message: str, **kwargs: Any) -> None:
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        ...

    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs: Any
    ) -> None:
        ...

    def critical(self, message: str, **kwargs: Any) -> None:
        ...

    def exception(self, message: str, **kwargs: Any) -> None:
        ...
