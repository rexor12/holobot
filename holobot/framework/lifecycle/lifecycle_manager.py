from .lifecycle_manager_interface import LifecycleManagerInterface
from holobot.sdk.exceptions import AggregateError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import ILoggerFactory
from typing import Tuple

@injectable(LifecycleManagerInterface)
class LifecycleManager(LifecycleManagerInterface):
    def __init__(
        self,
        startables: Tuple[StartableInterface, ...],
        logger_factory: ILoggerFactory
    ) -> None:
        self.__startables: Tuple[StartableInterface, ...] = startables
        self.__logger = logger_factory.create(LifecycleManager)
    
    async def start_all(self):
        errors = []
        for startable in self.__startables:
            try:
                await startable.start()
            except BaseException as error:
                errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        self.__logger.info("Successfully started all services")
    
    async def stop_all(self):
        errors = []
        for startable in self.__startables:
            try:
                await startable.stop()
            except BaseException as error:
                errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        self.__logger.info("Successfully stopped all services")
