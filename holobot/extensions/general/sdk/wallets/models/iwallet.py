from typing import Protocol

from .wallet_id import WalletId

class IWallet(Protocol):
    """Represents a user's wallet."""

    identifier: WalletId
    """The identifier of the wallet."""

    amount: int
    """The amount of the currency the user has."""
