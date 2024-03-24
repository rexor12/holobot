from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class AvatarOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    ArtworkArtistName: str = "Unknown"
