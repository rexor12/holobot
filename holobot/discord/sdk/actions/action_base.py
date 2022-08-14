from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class ActionBase:
    """Abstract base class for actions."""

    suppress_user_mentions: bool = False
    """Determines whether user mentions should avoid sending a notification."""
