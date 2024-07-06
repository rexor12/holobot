from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class GeneralOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Steam"

    StoreAppPageUrl: str = ""
    """The template format of the Steam Store's page of an application.

    The application identifier is passed as "appid" to this formatted string.
    """

    SearchResultExpirationTime: int = 180
    """The amount of time, in seconds, after which a set of
    search results expire and the components become invalid.
    """

    AppDetailExpirationTime: int = 180
    """The amount of time, in seconds, after which cached app details expire."""
