from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.security.credential_manager_interface import CredentialManagerInterface, T
from os import environ
from typing import Callable, Optional

class EnvironmentCredentialManager(CredentialManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__()

    def get(self, name: str, default_value: Optional[T] = None, converter: Callable[[str], T] = str) -> Optional[T]:
        value = environ.get(name, None)
        return converter(value) if value is not None else default_value