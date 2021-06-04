from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import EnvironmentInterface
from holobot.sdk.system.models import Version

import os

ROOT_PATH: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@injectable(EnvironmentInterface)
class Environment(EnvironmentInterface):
    # NOTE: This version number is automatically updated on build by the script assign_version.yml.
    __version = Version(2, 0, 0, 137)

    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()
    
    @property
    def root_path(self) -> str:
        return ROOT_PATH

    @property
    def version(self) -> Version:
        return self.__version
