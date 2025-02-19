import os

from holobot.sdk.system.ienvironment import IEnvironment
from holobot.sdk.system.models.version import Version

class FakeEnvironment(IEnvironment):
    _ROOT_PATH = os.getcwd()

    @property
    def root_path(self) -> str:
        return self._ROOT_PATH

    @property
    def version(self) -> Version:
        return Version(1)

    @property
    def shard_id(self) -> int:
        return 10
