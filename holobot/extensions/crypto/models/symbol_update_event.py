from decimal import Decimal
from holobot.sdk.reactive.models import EventBase

class SymbolUpdateEvent(EventBase):
    def __init__(self, symbol: str, price: Decimal, previous_price: Decimal | None):
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
    def previous_price(self) -> Decimal | None:
        return self.__previous_price

    @previous_price.setter
    def previous_price(self, value: Decimal | None):
        self.__previous_price = value

    @property
    def has_increased(self) -> bool:
        return self.previous_price is None or self.price > self.previous_price

    @property
    def has_decreased(self) -> bool:
        return self.previous_price is None or self.price < self.previous_price
