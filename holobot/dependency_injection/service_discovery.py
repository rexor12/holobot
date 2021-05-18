from holobot.configs.configurator import Configurator
from holobot.configs.configurator_interface import ConfiguratorInterface
from holobot.database.database_manager import DatabaseManager
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.database.migration.migration_interface import MigrationInterface
from holobot.dependency_injection.providers.simple_service_provider import SimpleServiceProvider
from holobot.dependency_injection.service_collection import ServiceCollection
from holobot.display.discord import Discord
from holobot.display.display_interface import DisplayInterface
from holobot.extensions.crypto import AlertManager, AlertManagerInterface, CryptoUpdater
from holobot.extensions.crypto.database import AlertMigration, CryptoMigration
from holobot.extensions.crypto.models import SymbolUpdateEvent
from holobot.extensions.crypto.repositories import CryptoRepository, CryptoRepositoryInterface
from holobot.extensions.reminders import ReminderManager, ReminderManagerInterface, ReminderProcessor
from holobot.extensions.reminders.database import ReminderMigration
from holobot.extensions.reminders.repositories import ReminderRepository, ReminderRepositoryInterface
from holobot.lifecycle.lifecycle_manager import LifecycleManager
from holobot.lifecycle.lifecycle_manager_interface import LifecycleManagerInterface
from holobot.lifecycle.startable_interface import StartableInterface
from holobot.logging.console_log import ConsoleLog
from holobot.logging.log_interface import LogInterface
from holobot.network.http_client_pool import HttpClientPool
from holobot.network.http_client_pool_interface import HttpClientPoolInterface
from holobot.reactive.listener_interface import ListenerInterface
from holobot.system.environment import Environment
from holobot.system.environment_interface import EnvironmentInterface

# TODO Implement automatic service discovery. (Look at all those imports!)
# Maybe a good idea here is to put these in the module __init__.py files?
class ServiceDiscovery:
    def register_services(self, service_collection: ServiceCollection):
        provider = SimpleServiceProvider()
        # Core
        provider.register(EnvironmentInterface, Environment)
        provider.register(HttpClientPoolInterface, HttpClientPool)
        provider.register(LifecycleManagerInterface, LifecycleManager)
        provider.register(DatabaseManagerInterface, DatabaseManager)
        provider.register(DisplayInterface, Discord)
        provider.register(LogInterface, ConsoleLog)
        provider.register(ConfiguratorInterface, Configurator)

        # Crypto
        provider.register(CryptoRepositoryInterface, CryptoRepository)
        provider.register(MigrationInterface, CryptoMigration)
        provider.register(MigrationInterface, AlertMigration)
        provider.register(StartableInterface, CryptoUpdater)
        provider.register(ListenerInterface[SymbolUpdateEvent], AlertManager)
        provider.register(AlertManagerInterface, AlertManager)

        # Reminders
        provider.register(MigrationInterface, ReminderMigration)
        provider.register(ReminderRepositoryInterface, ReminderRepository)
        provider.register(ReminderManagerInterface, ReminderManager)
        provider.register(StartableInterface, ReminderProcessor)

        service_collection.add_provider(provider)
