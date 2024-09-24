
import asyncio

from holobot.framework.lifecycle import LifecycleManagerInterface
from holobot.sdk import KernelInterface
from holobot.sdk.database import IDatabaseManager
from holobot.sdk.integration import IntegrationInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.system import IEnvironment

@injectable(KernelInterface)
class Kernel(KernelInterface):
    def __init__(
        self,
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

    async def run(self) -> None:
        self.__logger.info("Starting application...", version=str(self.__environment.version))

        await self.__database_manager.upgrade_all()
        await self.__lifecycle_manager.start_all()

        self.__logger.debug("Starting integrations...", count=len(self.__integrations))
        for integration in self.__integrations:
            await integration.start()
        self.__logger.info("Started integrations", count=len(self.__integrations))

        try:
            stop_event = asyncio.Event()
            self.__logger.info("Application started")

            await stop_event.wait()
        except asyncio.exceptions.CancelledError:
            self.__logger.info("Shutting down due to the application runtime event being cancelled...")
        except KeyboardInterrupt:
            self.__logger.info("Shutting down due to keyboard interrupt...")
        finally:
            for integration in self.__integrations:
                await integration.stop()
            await self.__lifecycle_manager.stop_all()
        self.__logger.info("Successful shutdown")
