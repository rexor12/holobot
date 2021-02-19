from decimal import Decimal
from holobot.reactive.models.event_base import EventBase
from typing import Optional

class SymbolUpdateEvent(EventBase):
    def __init__(self, symbol: str, price: Decimal, previous_price: Optional[Decimal]):
        if not symbol or len(symbol) == 0:
            raise ValueError("The symbol must be specified.")
        self.symbol = symbol
        self.price = price
        self.previous_price = previous_price

    @property
    def symbol(self) -> str:
        return self.__symbol

    @symbol.setter
    def symbol(self, value: str):
        self.__symbol = value
    
    @property
    def price(self) -> Decimal:
        return self.__price

    @price.setter
    def price(self, value: Decimal):
        self.__price = value
    
    @property
    def previous_price(self) -> Optional[Decimal]:
        return self.__previous_price

    @previous_price.setter
    def previous_price(self, value: Optional[Decimal]):
        self.__previous_price = value