from ..models import PriceData

class CryptoRepositoryInterface:
    async def get_price(self, symbol: str) -> PriceData | None:
        raise NotImplementedError

    async def update_prices(self, prices: list[PriceData]):
        raise NotImplementedError
