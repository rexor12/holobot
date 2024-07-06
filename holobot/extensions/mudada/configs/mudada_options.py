from dataclasses import dataclass, field
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class MudadaOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Mudada"

    MuderaCurrencyCode: str = "MUDERATEST"
    """The code of the currency Kakera can be exchanged for and vice-versa."""

    KakeraExchangeChannelIds: set[str] = field(default_factory=set)
    """The identifiers of the channels
    where event Kakera can be exchanged for Mudera."""

    MuderaExchangeChannelIds: set[str] = field(default_factory=set)
    """The identifiers of the channels
    where Mudera can be exchanged for regular Kakera."""

    ExchangeQuotaPerUser: int = 0
    """The maximum amount of Kakera that each user can exchange for Mudera."""
