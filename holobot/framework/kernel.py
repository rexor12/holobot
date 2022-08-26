
import asyncio

from holobot.framework.lifecycle import LifecycleManagerInterface
from holobot.sdk import KernelInterface
from holobot.sdk.database import IDatabaseManager
from holobot.sdk.integration import IntegrationInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.system import IEnvironment
from holobot.sdk.utils import when_all

@injectable(KernelInterface)
class Kernel(KernelInterface):
    def __init__(self,
        logger_factory: ILoggerFactory,
        database_manager: IDatabaseManager,
        environment: IEnvironment,
        integrations: tuple[IntegrationInterface, ...],
        lifecycle_manager: LifecycleManagerInterface
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(Kernel)
        self.__database_manager = database_manager
        self.__environment = environment
        self.__integrations = integrations
        self.__lifecycle_manager = lifecycle_manager

    def run(self):
        self.__logger.info("Starting application...", version=str(self.__environment.version))

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.__database_manager.upgrade_all())
        event_loop.run_until_complete(self.__lifecycle_manager.start_all())

        self.__logger.debug("Starting integrations...", count=len(self.__integrations))
        integration_tasks = tuple(event_loop.create_task(integration.start()) for integration in self.__integrations)
        self.__logger.info("Started integrations", count=len(integration_tasks))

        try:
            self.__logger.info("Application started")
            event_loop.run_forever()
        except KeyboardInterrupt:
            self.__logger.info("Shutting down due to keyboard interrupt...")
            for integration in self.__integrations:
                event_loop.run_until_complete(integration.stop())
        finally:
            event_loop.run_until_complete(when_all(integration_tasks))
            event_loop.run_until_complete(self.__lifecycle_manager.stop_all())
            event_loop.stop()
            event_loop.close()
        self.__logger.info("Successful shutdown")
