from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class WaifuPicsoptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    CircuitBreakerFailureThreshold: int = 1
    CircuitBreakerRecoveryTime: int = 300
    RateLimiterRequestsPerInterval: int = 2
    RateLimiterInterval: int = 5
    Url: str = ""
