from asyncpg.connection import Connection
from holobot.caching.cache import ConcurrentCache
from holobot.crypto.models.symbol_update_event import SymbolUpdateEvent
from holobot.crypto.price_data import PriceData
from holobot.crypto.repositories.crypto_repository_interface import CryptoRepositoryInterface
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.logging.log_interface import LogInterface
from holobot.reactive.listener_interface import ListenerInterface
from typing import List, Optional

class CryptoRepository(CryptoRepositoryInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__database_manager: DatabaseManagerInterface = service_collection.get(DatabaseManagerInterface)
        self.__log = service_collection.get(LogInterface)
        self.__listeners: List[ListenerInterface[SymbolUpdateEvent]] = service_collection.get_all(ListenerInterface[SymbolUpdateEvent])
        self.__cache: ConcurrentCache[str, Optional[PriceData]] = ConcurrentCache()

    async def get_price(self, symbol: str) -> Optional[PriceData]:
        self.__log.debug(f"[CryptoRepository] Getting price... {{ Symbol = {symbol} }}")
        result = await self.__cache.get_or_add(symbol, self.__load)
        self.__log.debug(f"[CryptoRepository] Got price. {{ Symbol = {symbol} }}")
        return result
    
    async def update_prices(self, prices: List[PriceData]):
        self.__log.debug("[CryptoRepository] Updating prices...")
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                for price_data in prices:
                    await self.__cache.add_or_update(
                        price_data.symbol,
                        lambda _: self.__save(connection, price_data),
                        lambda _, previous: self.__save(connection, price_data, previous)
                    )
        self.__log.debug(f"[CryptoRepository] Updated prices. {{ SymbolCount = {len(prices)} }}")

    async def __load(self, symbol: str) -> Optional[PriceData]:
        self.__log.debug(f"[CryptoRepository] Loading price... {{ Symbol = {symbol} }}")
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await connection.fetchrow("SELECT price, timestamp FROM crypto_binance WHERE symbol = $1 ORDER BY timestamp DESC", symbol)
                self.__log.debug(f"[CryptoRepository] Loaded price. {{ Symbol = {symbol}, Exists = {result is not None} }}")
                return PriceData(symbol, result["price"], result["timestamp"]) if result is not None else None
    
    async def __save(self, connection: Connection, price_data: PriceData, previous: PriceData = None):
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
