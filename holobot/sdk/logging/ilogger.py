from typing import Optional, Protocol

class ILogger(Protocol):
    """Interface for a service used for writing logs.

    Where the logs appear depend on the implementation
    of the interface (such as the console or a file).
    """

    def trace(self, message: str, **kwargs) -> None:
        ...

    def debug(self, message: str, **kwargs) -> None:
        ...

    def info(self, message: str, **kwargs) -> None:
        ...

    def warning(self, message: str, **kwargs) -> None:
        ...

    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs
    ) -> None:
        ...

    def critical(self, message: str, **kwargs) -> None:
        ...

    def exception(self, message: str) -> None:
        ...
