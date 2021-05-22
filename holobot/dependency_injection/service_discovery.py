from .models import ExportMetadata
from ..display import Discord, DisplayInterface
from ..configs import Configurator, ConfiguratorInterface
from ..database import DatabaseManager, DatabaseManagerInterface
from ..dependency_injection import ServiceCollection
from ..dependency_injection.providers import SimpleServiceProvider
from ..lifecycle import LifecycleManager, LifecycleManagerInterface
from ..logging import ConsoleLog, LogInterface
from ..network import HttpClientPool, HttpClientPoolInterface
from ..system import Environment, EnvironmentInterface
from types import ModuleType
from typing import List, Tuple

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

        service_collection.add_provider(provider)

        self.register_services_by_module("holobot.extensions.crypto", service_collection)
        self.register_services_by_module("holobot.extensions.reminders", service_collection)
        self.register_services_by_module("holobot.extensions.todo_lists", service_collection)

    def register_services_by_module(self, package_name: str, service_collection: ServiceCollection) -> None:
        provider = SimpleServiceProvider()
        for metadata in ServiceDiscovery.__get_exports_iteratively(package_name):
            provider.register(metadata.contract_type, metadata.export_type)
            #print(f"[ServiceDiscovery] Registered service. {{ ContractType = {metadata.contract_type}, ExportType = {metadata.export_type} }}")
        service_collection.add_provider(provider)
    
    @staticmethod
    def __get_exports_iteratively(module_name: str) -> Tuple[ExportMetadata, ...]:
        metadatas: List[ExportMetadata] = []
        module_names: List[str] = [module_name]
        while len(module_names) > 0:
            module_name = module_names.pop()
            module = importlib.import_module(module_name)
            metadatas.extend(ServiceDiscovery.__get_exports(module))

            if (path := getattr(module, "__path__", None)) is None:
                continue

            for loader, name, is_package in pkgutil.walk_packages(path):
                if not is_package:
                    continue
                module_names.append(f"{module_name}.{name}")
        
        return tuple(metadatas)
    
    @staticmethod
    def __get_exports(module: ModuleType) -> Tuple[ExportMetadata, ...]:
        exports: List[ExportMetadata] = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            metadatas: List[ExportMetadata] = getattr(obj, ExportMetadata.PROPERTY_NAME, [])
            exports.extend(metadatas)

        return tuple(exports)
