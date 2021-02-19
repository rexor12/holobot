from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.logging.log_interface import LogInterface
from holobot.logging.log_level import LogLevel
from typing import Optional

class LogBase(LogInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.log_level = LogLevel.INFORMATION

    def write(self, level: LogLevel, message: str, error: Optional[Exception] = None):
        if level < self.log_level:
            return
        self._on_write(level, message, error)

    def trace(self, message: str):
        self.write(LogLevel.TRACE, message)

    def debug(self, message: str):
        self.write(LogLevel.DEBUG, message)

    def info(self, message: str):
        self.write(LogLevel.INFORMATION, message)

    def warning(self, message: str):
        self.write(LogLevel.WARNING, message)

    def error(self, message: str, error: Exception):
        self.write(LogLevel.ERROR, message, error)

    def critical(self, message: str, error: Exception):
        self.write(LogLevel.CRITICAL, message, error)
    
    def _on_write(self, level: LogLevel, message: str, error: Optional[Exception]):
        raise NotImplementedError