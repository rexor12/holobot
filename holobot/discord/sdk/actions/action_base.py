from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class ActionBase:
    """Abstract base class for actions."""
