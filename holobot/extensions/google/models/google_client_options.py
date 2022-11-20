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

    MaxSearchResultsPerQuery: int = 20
    """The maximum number of results to be returned for each query.

    Due to a limitation imposed by Google, this value cannot be larger than 100.
    """

    SearchResultExpirationTime: int = 180
    """The amount of time, in seconds, after which a set of
    search results expire and the components become invalid.
    """

    ServiceAccountCredentialFile: str = ""
    """The path of the file that holds the Google Cloud service account credentials."""
