from ..enums import PriceDirection
from decimal import Decimal

class Alert:
    def __init__(self, symbol: str, direction: PriceDirection, price: Decimal):
        self.symbol = symbol
        self.direction = direction
        self.price = price
    
    @property
    def symbol(self) -> str:
        return self.__symbol
    
    @symbol.setter
    def symbol(self, value: str):
        self.__symbol = value
    
    @property
    def direction(self) -> PriceDirection:
        return self.__direction
    
    @direction.setter
    def direction(self, value: PriceDirection):
        self.__direction = value

    @property
    def price(self) -> Decimal:
        return self.__price

    @price.setter
    def price(self, value: Decimal):
        self.__price = value
