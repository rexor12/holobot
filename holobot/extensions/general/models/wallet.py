from dataclasses import dataclass

from holobot.extensions.general.sdk.wallets.models import IWallet, WalletId
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class Wallet(AggregateRoot[WalletId], IWallet):
    """Represents a user's wallet."""

    amount: int
    """The amount of the currency the user has."""
