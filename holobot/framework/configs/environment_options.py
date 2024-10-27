from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class EnvironmentOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Core"

    IsDebug: bool = False
    LogLevel: str = "Information"
    HttpPoolSize: int = 100
    ResourceDirectoryPath: str = ""
