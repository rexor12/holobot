from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass(kw_only=True)
class GeneralOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    ProgressBarRedEmoji: str
    ProgressBarOrangeEmoji: str
    ProgressBarGreenEmoji: str
    RefreshRelationshipsAfterMinutes: int = 30
