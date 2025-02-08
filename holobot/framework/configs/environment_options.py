from dataclasses import dataclass, field
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class EnvironmentOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Core"

    IsDebug: bool = False
    LogLevel: str = "Information"
    HttpPoolSize: int = 100

    ResourceDirectoryPaths: list[str] = field(default_factory=list)
    """An optional list of directory paths that contain resource files.

    Note: Resources that appear later in this list take a higher priority.

    Note: If this list is empty, the default root path is used for finding resources.
    """

    AssetSlidingExpirationTimeInMinutes: int = 10
    """The amount of time, in minutes, after which an asset is unloaded.

    This is a sliding expiration window which means that the elapsed time
    is measured from the most recent access to the asset.
    """
