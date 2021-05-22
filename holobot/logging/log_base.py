from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.logging.log_interface import LogInterface
from holobot.logging.log_level import LogLevel
from typing import Optional

class LogBase(LogInterface):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        self.log_level = LogLevel.INFORMATION

    def write(self, level: LogLevel, message: str, error: Optional[Exception] = None) -> None:
        if level < self.log_level:
            return
        self._on_write(level, message, error)

    def trace(self, message: str) -> None:
        self.write(LogLevel.TRACE, message)

    def debug(self, message: str) -> None:
        self.write(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        self.write(LogLevel.INFORMATION, message)

    def warning(self, message: str) -> None:
        self.write(LogLevel.WARNING, message)

    def error(self, message: str, error: Exception) -> None:
        self.write(LogLevel.ERROR, message, error)

    def critical(self, message: str, error: Exception) -> None:
        self.write(LogLevel.CRITICAL, message, error)
    
    def _on_write(self, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        raise NotImplementedError