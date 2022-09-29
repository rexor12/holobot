from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class GoogleClientOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Google"

    GoogleSearchApiKey: str = ""
    GoogleSearchEngineId: str = ""
    CircuitBreakerFailureThreshold: int = 1
    CircuitBreakerRecoveryTime: int = 300
