from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class Wallet(AggregateRoot[int]):
    """Represents a Mudada wallet."""

    amount: int
    """The amount of the currency the user has."""
