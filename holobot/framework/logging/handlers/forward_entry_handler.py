from typing import Any, Callable, Dict

import logging

from holobot.framework.logging.formatters import DefaultExternalLogFormatterInstance
from holobot.sdk.logging import ILogger

_DEFAULT_WRITER: Callable[[ILogger, str], None] = lambda i, m: i.trace(m)

_LOG_WRITERS: Dict[int, Callable[[ILogger, str], None]] = {
    logging.CRITICAL: lambda i, m: i.critical(m),
    logging.ERROR: lambda i, m: i.error(m),
    logging.WARNING: lambda i, m: i.warning(m),
    logging.INFO: lambda i, m: i.info(m),
    logging.DEBUG: lambda i, m: i.debug(m),
    logging.NOTSET: _DEFAULT_WRITER
}

class ForwardEntryHandler(logging.Handler):
    def __init__(
        self,
        target: ILogger,
        formatter: Any = DefaultExternalLogFormatterInstance
    ) -> None:
        super().__init__()
        self.__target = target
        self.__formatter = formatter

    def emit(self, record):
        if (writer := _LOG_WRITERS.get(record.levelno)) is None:
            writer = _DEFAULT_WRITER
        writer(self.__target, self.__formatter.format(record))
