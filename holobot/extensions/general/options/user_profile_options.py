from dataclasses import dataclass, field
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class _ReputationTableItem:
    RequiredReputation: int
    Color: str = "#9d9d9d"

@dataclass
class _CustomBackgroundItem:
    Code: str
    RequiredReputation: int
    FileName: str

@dataclass
class UserProfileOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    ReputationTable: list[_ReputationTableItem] = field(default_factory=list)
    CustomBackgroundsPath: str = "resources/images/user_profiles/custom_backgrounds"
    CustomBackgrounds: list[_CustomBackgroundItem] = field(default_factory=list)
