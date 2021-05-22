from .models import ExportMetadata
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
# from holobot.extensions.reminders import ReminderManager, ReminderManagerInterface, ReminderProcessor
# from holobot.extensions.reminders.database import ReminderMigration
# from holobot.extensions.reminders.repositories import ReminderRepository, ReminderRepositoryInterface
from holobot.extensions.todo_lists import TodoItemManager, TodoItemManagerInterface
from holobot.extensions.todo_lists.database import TodoListsMigration
from holobot.extensions.todo_lists.repositories import TodoItemRepository, TodoItemRepositoryInterface
from types import ModuleType
from typing import List, Optional, Tuple

import importlib, inspect, pkgutil

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
        # provider.register(MigrationInterface, ReminderMigration)
        # provider.register(ReminderRepositoryInterface, ReminderRepository)
        # provider.register(ReminderManagerInterface, ReminderManager)
        # provider.register(StartableInterface, ReminderProcessor)

        service_collection.add_provider(provider)

        self.register_services_by_module("holobot.extensions.reminders", service_collection)

    def register_services_by_module(self, package_name: str, service_collection: ServiceCollection) -> None:
        provider = SimpleServiceProvider()
        for metadata in ServiceDiscovery.__get_exports_iteratively(package_name):
            provider.register(metadata.contract_type, metadata.export_type)
        service_collection.add_provider(provider)
    
    @staticmethod
    def __get_exports_iteratively(module_name: str) -> Tuple[ExportMetadata, ...]:
        metadatas: List[ExportMetadata] = []
        module_names: List[str] = [module_name]
        while len(module_names) > 0:
            module_name = module_names.pop()
            module = importlib.import_module(module_name)
            metadatas.extend(ServiceDiscovery.__get_exports(module))

            for loader, name, is_package in pkgutil.walk_packages(module.__path__):
                if not is_package:
                    continue
                module_names.append(f"{module_name}.{name}")
        
        return tuple(metadatas)
    
    @staticmethod
    def __get_exports(module: ModuleType) -> Tuple[ExportMetadata, ...]:
        exports: List[ExportMetadata] = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            metadata: Optional[ExportMetadata] = getattr(obj, ExportMetadata.PROPERTY_NAME, None)
            if metadata is not None:
                exports.append(metadata)

        return tuple(exports)
