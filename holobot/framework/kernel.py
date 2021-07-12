from .ioc import ServiceCollection, ServiceDiscovery
from holobot.framework.lifecycle import LifecycleManagerInterface
from holobot.sdk import KernelInterface
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.integration import IntegrationInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.logging.enums import LogLevel
from holobot.sdk.utils import when_all
from typing import Tuple

import asyncio

class Startup:
    # This is __main__.
    def __init__(self) -> None:
        event_loop = asyncio.get_event_loop()
        service_collection = ServiceCollection()
        # The idea here is to register the services for each extension independently,
        # however, today it doesn't make sense as they're still in the same package.
        # Therefore, for now we just register everything from the entire package.
        exports = ServiceDiscovery.get_exports("holobot")

@injectable(KernelInterface)
class Kernel(KernelInterface):
    def __init__(self,
        log: LogInterface,
        configurator: ConfiguratorInterface,
        database_manager: DatabaseManagerInterface,
        lifecycle_manager: LifecycleManagerInterface,
        integrations: Tuple[IntegrationInterface, ...]) -> None:
        super().__init__()
        self.__event_loop = asyncio.get_event_loop()
        self.__log = log.with_name("Framework", "Kernel")
        self.__log.set_global_log_level(LogLevel.parse(configurator.get("General", "LogLevel", "Information")))
        self.__database_manager = database_manager
        self.__lifecycle_manager = lifecycle_manager
        self.__integrations = integrations

    def run(self):
        self.__log.info("Starting application...")

        self.__event_loop.run_until_complete(self.__database_manager.upgrade_all())
        self.__event_loop.run_until_complete(self.__lifecycle_manager.start_all())

        self.__log.debug(f"Starting integrations... {{ Count = {len(self.__integrations)} }}")
        integration_tasks = tuple([self.__event_loop.create_task(integration.start()) for integration in self.__integrations])
        self.__log.info(f"Started integrations. {{ Count = {len(integration_tasks)} }}")

        try:
            self.__log.info("Application started.")
            self.__event_loop.run_forever()
        except KeyboardInterrupt:
            self.__log.info("Shutting down due to keyboard interrupt...")
            for integration in self.__integrations:
                self.__event_loop.run_until_complete(integration.stop())
        finally:
            self.__event_loop.run_until_complete(when_all(integration_tasks))
            self.__event_loop.run_until_complete(self.__lifecycle_manager.stop_all())
            self.__event_loop.stop()
            self.__event_loop.close()
        self.__log.info("Successful shutdown.")
