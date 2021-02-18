from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.security.credential_manager_interface import CredentialManagerInterface
from os import environ
from typing import Any, Type

class EnvironmentCredentialManager(CredentialManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__()

    def get(self, name: str, default_value: str = None, converter: Type = None) -> Any:
        value = environ.get(name, default_value)
        return converter(value) if converter is not None else value