import os

from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment
from holobot.sdk.system.models import Version

@injectable(IEnvironment)
class Environment(IEnvironment):
    _ROOT_PATH = os.getcwd()
    _VERSION = Version.from_file("VERSION")

    @property
    def root_path(self) -> str:
        return self._ROOT_PATH

    @property
    def version(self) -> Version:
        return self._VERSION

    # TODO Update this when sharding is implemented.
    @property
    def shard_id(self) -> int:
        return 0
