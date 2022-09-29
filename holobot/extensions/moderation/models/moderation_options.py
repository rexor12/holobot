from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class ModerationOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Moderation"

    ReasonLengthMin: int = 10
    ReasonLengthMax: int = 192
    DecayThresholdMin: int = 1800
    DecayThresholdMax: int = 2592000
    WarnCleanupInterval: int = 3600
    WarnCleanupDelay: int = 60
    MuteDurationMin: int = 60
    MuteDurationMax: int = 2592000
    MuteCleanupInterval: int = 60
    MuteCleanupDelay: int = 60
