from dataclasses import dataclass

from holobot.sdk.configs import OptionsDefinition

@dataclass
class SteamAppDetailsOptions(OptionsDefinition):
    section_name: str = "Steam"

    BaseUrl: str = ""
    """The base URL for the Steam AppDetails API."""

    CircuitBreakerFailureThreshold: int = 1
    """The number of failures after which the circuit is changed to open status."""

    CircuitBreakerRecoveryTime: int = 300
    """The duration, in seconds, after which the circuit is changed to half-open status."""
