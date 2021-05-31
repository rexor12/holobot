from datetime import datetime
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogBase, LogInterface
from holobot.sdk.logging.enums import LogLevel
from typing import Optional

@injectable(LogInterface)
class ConsoleLog(LogBase):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()

    def _on_write(self, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        final_message = f"[{level.name}] [{datetime.now():%Y%m%dT%H%M%S}] {message}"
        if error is not None:
            final_message += f"\n{error}"
        print(final_message)