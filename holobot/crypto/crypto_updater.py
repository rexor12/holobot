from aiohttp.client_exceptions import ClientConnectionError, ClientConnectorError
from asyncio.tasks import Task
from datetime import datetime
from decimal import Decimal
from holobot.crypto.price_data import PriceData
from holobot.crypto.repositories.crypto_repository_interface import CryptoRepositoryInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.lifecycle.startable_interface import StartableInterface
from holobot.network.exceptions.http_status_error import HttpStatusError
from holobot.network.exceptions.im_a_teapot_error import ImATeapotError
from holobot.network.exceptions.too_many_requests_error import TooManyRequestsError
from holobot.network.http_client_pool_interface import HttpClientPoolInterface
from holobot.network.resilience.circuit_broken_error import CircuitBrokenError
from holobot.network.resilience.async_circuit_breaker import AsyncCircuitBreaker
from holobot.threading.async_loop import AsyncLoop
from typing import List

import asyncio

FAILURE_THRESHOLD: int = 1
RECOVERY_TIMEOUT: int = 5 * 60
INITIAL_UPDATE_DELAY: int = 15
UPDATE_INTERVAL: int = 60
BINANCE_API_BASE_URL: str = "https://api.binance.com/api/v3/"

# Test values
# UPDATE_INTERVAL: int = 10
# BINANCE_API_BASE_URL: str = "http://localhost:8000/"

async def evaluate_error(circuit_breaker: AsyncCircuitBreaker, error: Exception):
    if (isinstance(error, (TooManyRequestsError, ImATeapotError))
        and (retry_after := error.attrs.get("retry_after", None)) is not None
        and isinstance(retry_after, int)):
        return retry_after
    return circuit_breaker.recovery_timeout

class CryptoUpdater(StartableInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__http_client_pool: HttpClientPoolInterface = service_collection.get(HttpClientPoolInterface)
        self.__crypto_repository: CryptoRepositoryInterface = service_collection.get(CryptoRepositoryInterface)
        self.__background_loop: AsyncLoop = None
        self.__background_task: Task = None
        self.__circuit_breaker: AsyncCircuitBreaker = AsyncCircuitBreaker(
            FAILURE_THRESHOLD, RECOVERY_TIMEOUT, evaluate_error
        )

    async def start(self):
        self.__background_loop = AsyncLoop(self.__update_prices, UPDATE_INTERVAL, INITIAL_UPDATE_DELAY)
        self.__background_task = asyncio.create_task(self.__background_loop())
        print(f"[CryptoUpdater] Started background task. {{ Delay = {INITIAL_UPDATE_DELAY}, Interval = {UPDATE_INTERVAL} }}")
        
    async def stop(self):
        loop = self.__background_loop
        if loop is not None:
            loop.cancel()
        task = self.__background_task
        if task is not None:
            await task
        print("[CryptoUpdater] Stopped background task.")
    
    # TODO Automatic detection of the addition/removal of a symbol.
    async def __update_prices(self):
        print(f"[CryptoUpdater] Updating prices...")
        try:
            prices = await self.__circuit_breaker(self.__get_symbol_prices)
            if len(prices) > 0:
                await self.__crypto_repository.update_prices(prices)
                print(f"[CryptoUpdater] Successfully updated the prices of {len(prices)} symbols.")
            else: print(f"[CryptoUpdater] Received no symbol price data.")
        except (TooManyRequestsError, ImATeapotError) as error:
            print((
                "[CryptoUpdater] Failed to update symbol prices due to rate limit violation."
                f" Will try again in {self.__circuit_breaker.time_to_recover} seconds.\n{error}"
            ))
        except HttpStatusError as error:
            print((
                "[CryptoUpdater] Binance failed to respond due to an internal server error."
                f" Will try again in {self.__circuit_breaker.time_to_recover} seconds.\n{error}"
            ))
        except (ClientConnectionError, ClientConnectorError, ConnectionRefusedError, TimeoutError) as error:
            print((
                "[CryptoUpdater] Failed to connect to the Binance API or PostgreSQL server."
                f" Will try again in {self.__circuit_breaker.time_to_recover} seconds.\n{error}"
            ))
        except CircuitBrokenError:
            pass
        except Exception as error:
            print(f"[CryptoUpdater] Encountered an unexpected exception. Updates will stop.\n{error}")
            raise

    async def __get_symbol_prices(self) -> List[PriceData]:
        result = await self.__http_client_pool.get(f"{BINANCE_API_BASE_URL}ticker/price")
        now = datetime.utcnow()
        return [PriceData(
            currency.get("symbol", ""),
            Decimal(currency.get("price", 0.0)),
            now
        ) for currency in result]