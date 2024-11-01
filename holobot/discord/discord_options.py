from dataclasses import dataclass, field
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class DiscordOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Core"

    BotToken: str = ""
    PaginatorPreviousEmoji: int | None = None
    PaginatorNextEmoji: int | None = None
    IsNetworkTraceEnabled: bool = False
