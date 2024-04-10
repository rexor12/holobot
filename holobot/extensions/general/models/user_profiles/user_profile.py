from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class UserProfile(AggregateRoot[str]):
    """Represents a user's profile."""

    reputation_points: int = 0
    """The number of reputation points the user has."""
