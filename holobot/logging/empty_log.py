from .log_base import LogBase
from .log_level import LogLevel
from ..dependency_injection import ServiceCollectionInterface
from typing import Optional

class EmptyLog(LogBase):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__(service_collection)

    def _on_write(self, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        pass