from .ioc import ServiceCollection, ServiceDiscovery
from holobot.framework.lifecycle import LifecycleManagerInterface
from holobot.sdk import KernelInterface
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.integration import IntegrationInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.logging.enums import LogLevel
from holobot.sdk.utils import when_all

import asyncio

class Kernel(KernelInterface):
    def run(self):
        event_loop = asyncio.get_event_loop()
        service_collection = ServiceCollection()
        service_collection.add_service(self, KernelInterface)
        # The idea here is to register the services for each extension independently,
        # however, today it doesn't make sense as they're still in the same package.
        # Therefore, for now we just register everything from the entire package.
        ServiceDiscovery.register_services_by_module("holobot", service_collection)
        # self.register_services_by_module("holobot.extensions.crypto", service_collection)
        
        log = service_collection.get(LogInterface).with_name("Framework", "Kernel")
        configurator = service_collection.get(ConfiguratorInterface)
        log.log_level = LogLevel.parse(configurator.get("General", "LogLevel", "Information"))
        log.info("[Kernel] Starting application...")

        event_loop.run_until_complete(service_collection.get(DatabaseManagerInterface).upgrade_all())

        lifecycle_manager = service_collection.get(LifecycleManagerInterface)
        event_loop.run_until_complete(lifecycle_manager.start_all())

        integrations = service_collection.get_all(IntegrationInterface)
        integration_tasks = tuple([event_loop.create_task(integration.start()) for integration in integrations])
        log.debug(f"[Kernel] Started integrations. {{ Count = {len(integration_tasks)} }}")

        try:
            log.info("[Kernel] Application started.")
            event_loop.run_forever()
        except KeyboardInterrupt:
            log.info("[Kernel] Shutting down due to keyboard interrupt...")
            for integration in integrations:
                event_loop.run_until_complete(integration.stop())
        finally:
            event_loop.run_until_complete(when_all(integration_tasks))
            event_loop.run_until_complete(lifecycle_manager.stop_all())
            event_loop.run_until_complete(service_collection.close())
            event_loop.stop()
            event_loop.close()
        log.info("[Kernel] Successful shutdown.")
