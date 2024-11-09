from dataclasses import dataclass
from datetime import datetime

@dataclass(kw_only=True)
class RankingInfo:
    """Basic information about a marriage."""

    user_id1: int
    """The identifier of one of the users."""

    user_id2: int
    """The identifier of the other user."""

    level: int
    """The current level of the relationship."""

    married_at: datetime
    """The date and time at which the relationship was established."""
