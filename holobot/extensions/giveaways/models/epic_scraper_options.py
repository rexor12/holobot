from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class EpicScraperOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Giveaways"

    CircuitBreakerFailureThreshold: int = 1
    """The number of failures after which the circuit is changed to open status."""

    CircuitBreakerRecoveryTime: int = 300
    """The duration, in seconds, after which the circuit is changed to half-open status."""

    Url: str = ""
    """The URL of the API that returns the giveaway information."""

    CountryCode: str = "US"
    """The country code to use when fetching the giveaway information."""

    ExecutionDelay: int = 5 * 60
    """The amount of time, in seconds, by which the execution of the scraper is delayed.

    The purpose of this is to avoid fetching the giveaway information before it's updated.
    """
