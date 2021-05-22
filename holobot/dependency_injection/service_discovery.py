from . import ServiceCollection
from .models import ExportMetadata
from .providers import SimpleServiceProvider
from types import ModuleType
from typing import List, Tuple

import importlib, inspect, pkgutil

class ServiceDiscovery:
    @staticmethod
    def register_services_by_module(package_name: str, service_collection: ServiceCollection) -> None:
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
