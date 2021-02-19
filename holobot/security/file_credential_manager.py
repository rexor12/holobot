from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.security.credential_manager_interface import CredentialManagerInterface, T
from typing import Callable, Dict, Optional

# TODO Move this to configuration.
CREDENTIALS_FILE_PATH = "./.env"

class FileCredentialManager(CredentialManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__()
        self.__credentials: Optional[Dict[str, str]] = None

    def get(self, name: str, default_value: Optional[T] = None, converter: Callable[[str], T] = str) -> Optional[T]:
        if not self.__credentials:
            self.__credentials = self.__load_credentials()
        value = self.__credentials.get(name, None)
        return converter(value) if value is not None else default_value

    def __load_credentials(self) -> Dict[str, str]:
        credentials: Dict[str, str] = {}
        with open(CREDENTIALS_FILE_PATH) as repository:
            for line in repository.read().splitlines():
                partitions = line.partition("=")
                credentials[partitions[0]] = partitions[2]
        print(f"[FileCredentialManager] Loaded credentials. {{ Count = {len(credentials.keys())} }}")
        return credentials