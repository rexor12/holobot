from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.logging.log_base import LogBase
from holobot.logging.log_level import LogLevel
from typing import Optional

class EmptyLog(LogBase):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__(service_collection)

    def _on_write(self, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        pass