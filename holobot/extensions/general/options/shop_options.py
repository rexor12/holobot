from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class ShopOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    MaxShopsPerServer: int = 2
    """The maximum number of custom shops allowed to be created by each server."""

    MaxItemsPerShop: int = 5
    """The maximum number of items allowed to be added to each custom shop."""
