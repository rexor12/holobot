from dataclasses import dataclass

@dataclass
class FeatureState:
    """Describes the state of a feature."""

    identifier: str
    """The identifier of the feature."""

    is_enabled: bool = True
    """Whether the feature is enabled or disabled."""
