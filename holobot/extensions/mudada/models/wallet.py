from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class Wallet(AggregateRoot[str]):
    """Represents a Mudada wallet."""

    identifier: str
    """The identifier of the user the wallet belongs to."""

    amount: int
    """The amount of the currency the user has."""
