from dataclasses import dataclass

from holobot.sdk.configs import OptionsDefinition

@dataclass
class SteamAppsOptions(OptionsDefinition):
    section_name: str = "Steam"

    BaseUrl: str = ""
    """The base URL for the ISteamApps API."""

    RefreshResolution: int = 30 # 3600
    """The interval, in seconds, at which apps are queried from the ISteamApps API."""

    RefreshDelay: int = 30
    """The duration, in seconds, after which the apps
    are queried from the ISteamApps API for the first time.
    """

    CircuitBreakerFailureThreshold: int = 1
    """The number of failures after which the circuit is changed to open status."""

    CircuitBreakerRecoveryTime: int = 300
    """The duration, in seconds, after which the circuit is changed to half-open status."""
