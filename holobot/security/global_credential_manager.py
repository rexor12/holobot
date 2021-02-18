from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.security.credential_manager_interface import CredentialManagerInterface
from holobot.security.global_credential_manager_interface import GlobalCredentialManagerInterface
from typing import Any, Type

class GlobalCredentialManager(GlobalCredentialManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__managers = service_collection.get_all(CredentialManagerInterface)
    
    def get(self, name: str, default_value: str = None, converter: Type = None) -> Any:
        value: str = None
        for manager in self.__managers:
            value = manager.get(name, None)
            if value is None:
                continue
        if value is None:
            return default_value
        return converter(value) if converter is not None else value