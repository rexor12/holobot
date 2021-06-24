from holobot.sdk.logging import LogBase, LogInterface
from holobot.sdk.logging.enums import LogLevel
from typing import Optional

class EmptyLog(LogBase):
    def __init__(self) -> None:
        super().__init__()

    def _on_write(self, logger: LogInterface, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        pass
