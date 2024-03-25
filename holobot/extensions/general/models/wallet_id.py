from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class WalletId(Identifier):
    user_id: str
    """The identifier of the owning user."""

    currency_id: int
    """The identifier of the associated currency."""

    server_id: str
    """The identifier of the server the wallet belongs to."""

    def __str__(self) -> str:
        return f"Wallet/{self.user_id}/{self.currency_id}/{self.server_id}"

    @staticmethod
    def create(user_id: str, currency_id: int, server_id: str | None) -> 'WalletId':
        return WalletId(
            user_id=user_id,
            currency_id=currency_id,
            server_id=server_id or "0"
        )
