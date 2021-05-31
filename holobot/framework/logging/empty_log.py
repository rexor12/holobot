from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.logging import LogBase
from holobot.sdk.logging.enums import LogLevel
from typing import Optional

class EmptyLog(LogBase):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()

    def _on_write(self, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        pass