from holobot.framework.logging import DefaultLogger
from holobot.sdk.logging import ILogger, ILoggerFactory
from holobot.sdk.logging.enums import LogLevel

class TestLoggerFactory(ILoggerFactory):
    def create(self, target_type: type) -> ILogger:
        return DefaultLogger(target_type.__name__, lambda: LogLevel.DEBUG)
