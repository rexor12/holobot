from abc import abstractmethod
from holobot.crypto.price_data import PriceData
from typing import List

class CryptoRepositoryInterface:
    # TODO Add abstractmethod decorators.
    # @abstractmethod
    async def get_price(self, symbol: str) -> PriceData or None:
        raise NotImplementedError
    
    async def update_prices(self, prices: List[PriceData]):
        raise NotImplementedError