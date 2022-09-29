from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class ReminderProcessingOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Reminders"

    IsEnabled: bool = True
    Resolution: int = 60
    Delay: int = 30
