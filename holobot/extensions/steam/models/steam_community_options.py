from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class SteamCommunityOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Steam"

    BaseUrl: str = ""
    """The base URL for the Steam Community API."""

    CircuitBreakerFailureThreshold: int = 1
    """The number of failures after which the circuit is changed to open status."""

    CircuitBreakerRecoveryTime: int = 300
    """The duration, in seconds, after which the circuit is changed to half-open status."""

    MaxSearchResults: int = 5
    """The number of search results that are kept at maximum.

    The Steam end-point may decide to return fewer results.
    """
