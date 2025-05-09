from dataclasses import dataclass, field
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass(kw_only=True)
class GeneralOptions(OptionsDefinition):
    section_name: ClassVar[str] = "General"

    ProgressBarRedEmoji: str
    ProgressBarOrangeEmoji: str
    ProgressBarGreenEmoji: str
    ProgressBarEmptyEmoji: str
    RefreshRelationshipsAfterMinutes: int = 30

    MarriageActivityLastTierCooldownSeconds: int = 60
    """The time, in seconds, that must elapse between marriage related activities
    for the relationship to receive experience points.
    """

    MarriageActivityExpTiers: list[int] = field(default_factory=list)
    """The experience points marriage activities reward for each tier."""

    MarriageActivityExpTable: list[int] = field(default_factory=list)
    """The list of experience points required for each level.

    This list must begin with level 2, because level 1 is the default level.
    """

    MatchMarriageBonusScore: str = ""
    """The list of bonus minimum scores by level.

    This is a string in the following format: level:bonus;level:bonus;...
    """

    MarriageEmbedThumbnailUrl: str | None = None
    """The URL of the thumbnail image to display in the marriage embed."""

    FortuneCookieEmbedThumbnailUrl: str | None = None
    """The URL of the thumbnail image to display in the fortune cookie embed."""

    ShopEmbedThumbnailUrl: str | None = None
    """ The URL of the thumbnail image to display in the shop embed."""
