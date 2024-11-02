from dataclasses import dataclass

@dataclass(kw_only=True)
class RestrictionBase:
    """Abstract base class for restrictions."""
