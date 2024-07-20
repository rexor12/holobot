from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class RockPaperScissorsOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    RockEmojiId: int
    RockEmojiName: str
    PaperEmojiId: int
    PaperEmojiName: str
    ScissorsEmojiId: int
    ScissorsEmojiName: str
