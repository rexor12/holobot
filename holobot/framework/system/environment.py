import os

from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment
from holobot.sdk.system.models import Version

@injectable(IEnvironment)
class Environment(IEnvironment):
    # NOTE: This version number is automatically updated on build by the script assign_version.yml.
    _VERSION = Version.from_file("VERSION")
    _ROOT_PATH = os.getcwd()

    @property
    def root_path(self) -> str:
        return self._ROOT_PATH

    @property
    def version(self) -> Version:
        return self._VERSION
