from dataclasses import dataclass

@dataclass(kw_only=True)
class ComponentStateBase:
    """Base class for component states."""

    identifier: str
    """The identifier of the component this state belongs to."""

    owner_id: str
    """The identifier of the user the component state belongs to."""
