from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class EpicScraperOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Giveaways"

    CircuitBreakerFailureThreshold: int = 1
    CircuitBreakerRecoveryTime: int = 300
    Url: str = ""
    CountryCode: str = "US"
