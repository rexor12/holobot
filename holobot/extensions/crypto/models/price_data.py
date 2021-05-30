from datetime import datetime
from decimal import Decimal

class PriceData:
    def __init__(self, symbol: str, price: Decimal, timestamp: datetime):
        self.symbol: str = symbol
        self.price: Decimal = price
        self.timestamp: datetime = timestamp
