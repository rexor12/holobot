from .log_interface import LogInterface
from .enums import LogLevel
from threading import Lock
from typing import Dict, Optional

class ChildLog(LogInterface):
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

class LogBase(LogInterface):
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__()
        self.__lock: Lock = Lock()
        self.__children: Dict[str, ChildLog] = {}
        self.name = name
        self.log_level = LogLevel.INFORMATION
    
    def set_global_log_level(self, log_level: LogLevel):
        self.log_level = log_level
        for child in self.__children.values():
            child.log_level = log_level
    
    def with_name(self, module: str, name: str) -> LogInterface:
        if not module or not name:
            raise ValueError("The module and logger names must be specified.")
        
        with self.__lock:
            if (value := self.__children.get(name, None)) is not None:
                return value
            self.__children[name] = value = ChildLog(self, name, self.with_name, self.__internal_write)
            return value

    def write(self, level: LogLevel, message: str, error: Optional[Exception] = None) -> None:
        self.__internal_write(self, level, message, error)
    
    def _on_write(self, logger: LogInterface, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        raise NotImplementedError
    
    def __internal_write(self, logger: LogInterface, level: LogLevel, message: str, error: Optional[Exception] = None) -> None:
        if not message:
            raise ValueError("The message must be specified.")

        if level < logger.log_level:
            return
        self._on_write(logger, level, message, error)
