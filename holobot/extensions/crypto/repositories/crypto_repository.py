from .crypto_repository_interface import CryptoRepositoryInterface
from ..models import PriceData, SymbolUpdateEvent
from asyncpg.connection import Connection
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener
from typing import List, Optional, Tuple

@injectable(CryptoRepositoryInterface)
class CryptoRepository(CryptoRepositoryInterface):
    def __init__(self,
        configurator: ConfiguratorInterface,
        database_manager: DatabaseManagerInterface,
        logger_factory: ILoggerFactory,
        listeners: Tuple[IListener[SymbolUpdateEvent], ...]
    ) -> None:
        self.__configurator: ConfiguratorInterface = configurator
        self.__database_manager: DatabaseManagerInterface = database_manager
        self.__log = logger_factory.create(CryptoRepository)
        self.__listeners: Tuple[IListener[SymbolUpdateEvent], ...] = listeners
        self.__cache: ConcurrentCache[str, Optional[PriceData]] = ConcurrentCache()

    async def get_price(self, symbol: str) -> Optional[PriceData]:
        self.__log.debug(f"Getting price... {{ Symbol = {symbol} }}")
        result = await self.__cache.get_or_add(symbol, self.__load)
        self.__log.debug(f"Got price. {{ Symbol = {symbol} }}")
        return result

    async def update_prices(self, prices: List[PriceData]):
        self.__log.debug("Updating prices...")
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                for price_data in prices:
                    await self.__cache.add_or_update(
                        price_data.symbol,
                        lambda _: self.__save(connection, price_data),
                        lambda _, previous: self.__save(connection, price_data, previous)
                    )
        self.__log.debug(f"Updated prices. {{ SymbolCount = {len(prices)} }}")

    async def __load(self, symbol: str) -> Optional[PriceData]:
        self.__log.debug(f"Loading price... {{ Symbol = {symbol} }}")
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await connection.fetchrow("SELECT price, timestamp FROM crypto_binance WHERE symbol = $1 ORDER BY timestamp DESC", symbol)
                self.__log.debug(f"Loaded price. {{ Symbol = {symbol}, Exists = {result is not None} }}")
                return PriceData(symbol, result["price"], result["timestamp"]) if result is not None else None

    async def __save(self, connection: Connection, price_data: PriceData, previous: Optional[PriceData] = None):
        # TODO Implement this persistence toggle in a more efficient way, so that no database connection is made.
        if self.__configurator.get("Crypto", "PersistPrices", True):
            await connection.execute("INSERT INTO crypto_binance (symbol, timestamp, price) VALUES ($1, $2, $3)", price_data.symbol, price_data.timestamp, price_data.price)
        if previous is not None and price_data.price == previous.price:
            return
        # TODO Detach notifications from the current connection.
        for listener in self.__listeners:
            await listener.on_event(SymbolUpdateEvent(
                price_data.symbol,
                price_data.price,
                previous.price if previous is not None else None
            ))
        return price_data
