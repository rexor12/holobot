from dataclasses import dataclass, field
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition
from .group_configuration import GroupConfiguration

@dataclass
class CommandOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Admin"

    CommandGroups: list[GroupConfiguration] = field(default_factory=list)
