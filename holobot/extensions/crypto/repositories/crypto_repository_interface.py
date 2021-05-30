from ..models import PriceData
from typing import List, Optional

class CryptoRepositoryInterface:
    async def get_price(self, symbol: str) -> Optional[PriceData]:
        raise NotImplementedError
    
    async def update_prices(self, prices: List[PriceData]):
        raise NotImplementedError
