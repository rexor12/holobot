from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class ReminderOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Reminders"

    RemindersPerUserMax: int = 5
    MessageLengthMin: int = 10
    MessageLengthMax: int = 120
