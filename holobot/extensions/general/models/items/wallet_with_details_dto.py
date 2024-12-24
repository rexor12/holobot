from dataclasses import dataclass

@dataclass(kw_only=True)
class WalletWithDetailsDto:
    user_id: int
    server_id: int
    currency_id: int
    amount: int
    currency_name: str
    currency_emoji_id: int
    currency_emoji_name: str
