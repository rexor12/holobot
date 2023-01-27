from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILogger, ILoggerFactory, ILoggerManager
from holobot.sdk.logging.enums import LogLevel
from holobot.sdk.utils import get_fully_qualified_name
from .default_logger import DefaultLogger

@injectable(ILoggerFactory)
class DefaultLoggerFactory(ILoggerFactory):
    def __init__(self, logger_manager: ILoggerManager) -> None:
        super().__init__()
        self.__logger_manager = logger_manager

    def create(self, target_type: type) -> ILogger:
        return DefaultLogger(
            get_fully_qualified_name(target_type),
            self.__get_min_log_level
        )

    def __get_min_log_level(self) -> LogLevel:
        return self.__logger_manager.get_min_log_level()
