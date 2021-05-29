from .enums.log_level import LogLevel
from typing import Optional

class LogInterface:
    @property
    def log_level(self) -> LogLevel:
        return self.__log_level
    
    @log_level.setter
    def log_level(self, value: LogLevel):
        self.__log_level = value

    def write(self, level: LogLevel, message: str, error: Optional[Exception] = None) -> None:
        raise NotImplementedError

    def trace(self, message: str) -> None:
        raise NotImplementedError

    def debug(self, message: str) -> None:
        raise NotImplementedError

    def info(self, message: str) -> None:
        raise NotImplementedError

    def warning(self, message: str) -> None:
        raise NotImplementedError

    def error(self, message: str, error: Exception) -> None:
        raise NotImplementedError

    def critical(self, message: str, error: Exception) -> None:
        raise NotImplementedError