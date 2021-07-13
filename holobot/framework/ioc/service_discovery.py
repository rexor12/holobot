from holobot.sdk.ioc.models import ExportMetadata
from types import ModuleType
from typing import List, Tuple

import importlib, inspect, pkgutil

class ServiceDiscovery:
    @staticmethod
    def get_exports(module_name: str) -> Tuple[ExportMetadata, ...]:
        metadatas: List[ExportMetadata] = []
        module_names: List[str] = [module_name]
        while len(module_names) > 0:
            module_name = module_names.pop()
            #print(f"[ServiceDiscovery] Loading module... {{ Name = {module_name} }}")
            module = importlib.import_module(module_name)
            metadatas.extend(ServiceDiscovery.__get_exports(module))

            if (path := getattr(module, "__path__", None)) is None:
                continue

            #print(f"[ServiceDiscovery] Walking path... {{ Path = {path} }}")
            for loader, name, is_package in pkgutil.walk_packages(path):
                if not is_package:
                    continue
                # TODO Temporary. Remove this before merge.
                if name == "discord" or name == "extensions":
                    continue
                #print(f"[ServiceDiscovery] Found additional package. {{ Name = {name}, Parent = {module_name} }}")
                module_names.append(f"{module_name}.{name}")
        
        return tuple(metadatas)
    
    @staticmethod
    def __get_exports(module: ModuleType) -> Tuple[ExportMetadata, ...]:
        exports: List[ExportMetadata] = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            metadatas: List[ExportMetadata] = getattr(obj, ExportMetadata.PROPERTY_NAME, [])
            exports.extend(metadatas)

        return tuple(exports)
