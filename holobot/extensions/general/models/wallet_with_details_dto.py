from dataclasses import dataclass

from .wallet_id import WalletId

@dataclass(kw_only=True)
class WalletWithDetailsDto:
    wallet_id: WalletId
    amount: int
    currency_name: str
    currency_emoji_id: int
    currency_emoji_name: str
