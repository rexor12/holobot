from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class FortuneCookie(AggregateRoot[int]):
    """Represents a fortune cookie."""

    identifier: int = -1
    """The identifier of the entity."""

    message: str
    """The wisdom hidden inside the fortune cookie."""
