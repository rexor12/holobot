from typing import Tuple


from .lifecycle_manager_interface import LifecycleManagerInterface
from holobot.sdk.diagnostics import IExecutionContextFactory
from holobot.sdk.exceptions import AggregateError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory

@injectable(LifecycleManagerInterface)
class LifecycleManager(LifecycleManagerInterface):
    def __init__(
        self,
        execution_context_factory: IExecutionContextFactory,
        logger_factory: ILoggerFactory,
        startables: Tuple[IStartable, ...]
    ) -> None:
        self.__execution_context_factory = execution_context_factory
        self.__logger = logger_factory.create(LifecycleManager)
        self.__startables = startables
    
    async def start_all(self):
        with self.__execution_context_factory.create("Started startables", "Started all"):
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
        with self.__execution_context_factory.create("Stopped startables", "Stopped all"):
            errors = []
            for startable in self.__startables:
                try:
                    await startable.stop()
                except BaseException as error:
                    errors.append(error)
            if len(errors) > 0:
                raise AggregateError(errors)
        self.__logger.info("Successfully stopped all services")
