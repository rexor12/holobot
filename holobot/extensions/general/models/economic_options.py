from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class EconomicOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    CurrenciesEmbedThumbnailUrl: str | None = None
    """The URL of the thumbnail image to display in the currencies embed."""

    WalletEmbedThumbnailUrl: str | None = None
    """The URL of the thumbnail image to display in the wallet embed."""

    MaxCurrencyCountPerServer: int = 2
    """The maximum number of custom currencies a server can have at a time."""
