from ..display import Discord, DisplayInterface
from ..configs import Configurator, ConfiguratorInterface
from ..database import DatabaseManager, DatabaseManagerInterface
from ..database.migration import MigrationInterface
from ..dependency_injection import ServiceCollection
from ..dependency_injection.providers import SimpleServiceProvider
from ..lifecycle import LifecycleManager, LifecycleManagerInterface, StartableInterface
from ..logging import ConsoleLog, LogInterface
from ..network import HttpClientPool, HttpClientPoolInterface
from ..reactive import ListenerInterface
from ..system import Environment, EnvironmentInterface
from holobot.extensions.crypto import AlertManager, AlertManagerInterface, CryptoUpdater
from holobot.extensions.crypto.database import AlertMigration, CryptoMigration
from holobot.extensions.crypto.models import SymbolUpdateEvent
from holobot.extensions.crypto.repositories import CryptoRepository, CryptoRepositoryInterface
from holobot.extensions.reminders import ReminderManager, ReminderManagerInterface, ReminderProcessor
from holobot.extensions.reminders.database import ReminderMigration
from holobot.extensions.reminders.repositories import ReminderRepository, ReminderRepositoryInterface
from holobot.extensions.todo_lists import TodoItemManager, TodoItemManagerInterface
from holobot.extensions.todo_lists.database import TodoListsMigration
from holobot.extensions.todo_lists.repositories import TodoItemRepository, TodoItemRepositoryInterface

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

        # Dev extension
        provider.register(MigrationInterface, TodoListsMigration)
        provider.register(TodoItemRepositoryInterface, TodoItemRepository)
        provider.register(TodoItemManagerInterface, TodoItemManager)

        # Crypto extension
        provider.register(CryptoRepositoryInterface, CryptoRepository)
        provider.register(MigrationInterface, CryptoMigration)
        provider.register(MigrationInterface, AlertMigration)
        provider.register(StartableInterface, CryptoUpdater)
        provider.register(ListenerInterface[SymbolUpdateEvent], AlertManager)
        provider.register(AlertManagerInterface, AlertManager)

        # Reminders extension
        provider.register(MigrationInterface, ReminderMigration)
        provider.register(ReminderRepositoryInterface, ReminderRepository)
        provider.register(ReminderManagerInterface, ReminderManager)
        provider.register(StartableInterface, ReminderProcessor)

        service_collection.add_provider(provider)
