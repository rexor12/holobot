from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot

@dataclass
class FeatureState(AggregateRoot[str]):
    """Describes the state of a feature."""

    identifier: str
    """The identifier of the feature."""

    is_enabled: bool = True
    """Whether the feature is enabled or disabled."""
