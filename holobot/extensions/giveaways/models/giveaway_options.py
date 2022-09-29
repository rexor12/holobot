from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class GiveawayOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Giveaways"

    EnableScrapers: bool = True
    RunnerResolution: int = 60
    RunnerDelay: int = 40
    AnnouncementServerId: str = ""
    AnnouncementChannelId: str = ""
