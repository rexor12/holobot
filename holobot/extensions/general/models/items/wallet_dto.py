from dataclasses import dataclass

@dataclass(kw_only=True)
class WalletDto:
    currency_id: int
    amount: int
