from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class OpenWeatherOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Weather"

    ApiKey: str = ""
    CircuitBreakerFailureThreshold: int = 1
    CircuitBreakerRecoveryTime: int = 300
    ApiGatewayBaseUrl: str = ""
    ConditionImageBaseUrl: str = ""
    IconUrl: str = ""
