from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class ShopOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    MaxShopsPerServer: int = 2
