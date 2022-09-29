from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class DiscordOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Core"

    BotToken: str = ""
    DevelopmentServerId: int = 0
