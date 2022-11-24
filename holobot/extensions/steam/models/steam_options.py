from dataclasses import dataclass

from holobot.sdk.configs import OptionsDefinition

@dataclass
class SteamOptions(OptionsDefinition):
    section_name: str = "Steam"

    MaxSearchResults: int = 10
    """The maximum number of search application results per user."""
