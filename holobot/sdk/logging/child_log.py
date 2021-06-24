from .log_base import LogBase
from .log_interface import LogInterface
from .enums import LogLevel
from typing import Optional

class ChildLog(LogInterface):
    """Internal class for child loggers.

    This internal class is meant to be used by the ``LogBase`` class only.
    """

    def __init__(self, parent: 'LogBase', name: str, child_factory, write_callback) -> None:
        super().__init__()
        self.name = name
        self.log_level = parent.log_level
        self.__parent = parent
        self.__child_factory = child_factory
        self.__write_callback = write_callback
    
    def set_global_log_level(self, log_level: LogLevel):
        self.__parent.set_global_log_level(log_level)
    
    def with_name(self, module: str, name: str) -> LogInterface:
        return self.__child_factory(module, name)
    
    def write(self, level: LogLevel, message: str, error: Optional[Exception] = None) -> None:
        self.__write_callback(self, level, message, error)
