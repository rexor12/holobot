from dataclasses import dataclass

@dataclass(kw_only=True)
class ExchangeInfo:
    currency_id: int
    previous_amount: int
    new_amount: int
