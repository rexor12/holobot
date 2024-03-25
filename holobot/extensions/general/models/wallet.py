from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot
from .wallet_id import WalletId

@dataclass(kw_only=True)
class Wallet(AggregateRoot[WalletId]):
    """Represents a user's wallet."""

    amount: int
    """The amount of the currency the user has."""
