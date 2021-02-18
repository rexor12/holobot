from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.security.credential_manager_interface import CredentialManagerInterface
from typing import Any, Dict, Type

# TODO Move this to configuration.
CREDENTIALS_FILE_PATH = "./.env"

class FileCredentialManager(CredentialManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__()
        self.__credentials: Dict[str, str] = None

    def get(self, name: str, default_value: str = None, converter: Type = None) -> Any:
        if self.__credentials is None:
            self.__credentials = self.__load_credentials()
        value = self.__credentials.get(name, default_value)
        if value is None or len(value) == 0:
            return default_value
        return converter(value) if converter is not None else value

    def __load_credentials(self) -> Dict[str, str]:
        credentials: Dict[str, str] = {}
        with open(CREDENTIALS_FILE_PATH) as repository:
            for line in repository.read().splitlines():
                partitions = line.partition("=")
                credentials[partitions[0]] = partitions[2]
        print(f"[FileCredentialManager] Loaded credentials. {{ Count = {len(credentials.keys())} }}")
        return credentials