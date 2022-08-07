from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment
from holobot.sdk.system.models import Version

import os

ROOT_PATH: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@injectable(IEnvironment)
class Environment(IEnvironment):
    # NOTE: This version number is automatically updated on build by the script assign_version.yml.
    __version = Version(4, 0, 0, 406)

    @property
    def root_path(self) -> str:
        return ROOT_PATH

    @property
    def version(self) -> Version:
        return self.__version
