from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.security.credential_manager_interface import CredentialManagerInterface, T
from holobot.security.global_credential_manager_interface import GlobalCredentialManagerInterface
from typing import Callable, Optional

class GlobalCredentialManager(GlobalCredentialManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__managers = service_collection.get_all(CredentialManagerInterface)
    
    def get(self, name: str, default_value: Optional[T] = None, converter: Callable[[str], T] = str) -> Optional[T]:
        value: Optional[T] = None
        for manager in self.__managers:
            value = manager.get(name, None, converter)
            if not value:
                continue
        return value if value is not None else default_value