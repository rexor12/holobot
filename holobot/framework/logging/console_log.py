from datetime import datetime
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogBase, LogInterface
from holobot.sdk.logging.enums import LogLevel
from typing import Optional

import tzlocal

@injectable(LogInterface)
class ConsoleLog(LogBase):
    """A logger that formats and writes messages to the console."""

    def _on_write(self, logger: LogInterface, level: LogLevel, message: str, error: Optional[Exception]) -> None:
        current_time = datetime.now(tzlocal.get_localzone())
        formatted_name = logger.name if logger.name is not None else ""
        formatted_message = f"{level.name}\t{formatted_name}\t{current_time:%Y%m%dT%H%M%S%z}\t{message}"
        if error is not None:
            formatted_message += f"\n{error}"
        print(formatted_message)
