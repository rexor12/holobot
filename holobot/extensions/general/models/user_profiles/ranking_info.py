from dataclasses import dataclass

@dataclass(kw_only=True)
class RankingInfo:
    """Basic information about a user profile."""

    user_id: int
    """The identifier of the user the profile belongs to."""

    reputation_points: int
    """The number of reputation points the user has."""
