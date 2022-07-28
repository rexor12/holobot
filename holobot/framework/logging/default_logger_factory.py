from typing import Any, Type

from .default_logger import DefaultLogger
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILogger, ILoggerFactory
from holobot.sdk.utils import get_fully_qualified_name

@injectable(ILoggerFactory)
class DefaultLoggerFactory(ILoggerFactory):
    def create(self, target_type: Type[Any]) -> ILogger:
        return DefaultLogger(get_fully_qualified_name(target_type))
