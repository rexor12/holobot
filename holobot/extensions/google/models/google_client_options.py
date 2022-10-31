from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class GoogleClientOptions(OptionsDefinition):
    """Options for the Google client."""

    section_name: ClassVar[str] = "Google"

    GoogleSearchApiKey: str = ""
    GoogleSearchEngineId: str = ""
    CircuitBreakerFailureThreshold: int = 1
    CircuitBreakerRecoveryTime: int = 300

    ServiceAccountCredentialFile: str = ""
    """The path of the file that holds the Google Cloud service account credentials."""
