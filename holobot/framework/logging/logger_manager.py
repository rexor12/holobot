from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerManager
from holobot.sdk.logging.enums import LogLevel
from .logger_wrapper import LoggerWrapper

@injectable(ILoggerManager)
class LoggerManager(ILoggerManager):
    def get_min_log_level(self) -> LogLevel:
        return LoggerWrapper.get_min_log_level()

    def set_min_log_level(self, min_log_level: LogLevel) -> None:
        LoggerWrapper.set_min_log_level(min_log_level)
