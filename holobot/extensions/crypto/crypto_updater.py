from .models import PriceData
from .repositories import CryptoRepositoryInterface
from aiohttp.client_exceptions import ClientConnectionError, ClientConnectorError
from asyncio.exceptions import TimeoutError as AsyncIoTimeoutError
from asyncio.tasks import Task
from datetime import datetime
from decimal import Decimal
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, ImATeapotError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreaker
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.threading import AsyncLoop
from typing import List, Optional

import asyncio

FAILURE_THRESHOLD: int = 1
RECOVERY_TIMEOUT: int = 5 * 60
INITIAL_UPDATE_DELAY: int = 15
UPDATE_INTERVAL: int = 60
BINANCE_API_BASE_URL: str = "https://api.binance.com/api/v3/"

async def evaluate_error(circuit_breaker: AsyncCircuitBreaker, error: Exception):
    if (isinstance(error, (TooManyRequestsError, ImATeapotError))
        and error.retry_after is not None
        and isinstance(error.retry_after, int)):
        return error.retry_after
    return circuit_breaker.recovery_timeout

@injectable(StartableInterface)
class CryptoUpdater(StartableInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__http_client_pool: HttpClientPoolInterface = service_collection.get(HttpClientPoolInterface)
        self.__crypto_repository: CryptoRepositoryInterface = service_collection.get(CryptoRepositoryInterface)
        self.__configurator: ConfiguratorInterface = service_collection.get(ConfiguratorInterface)
        self.__log = service_collection.get(LogInterface)
        self.__background_loop: Optional[AsyncLoop] = None
        self.__background_task: Optional[Task] = None
        self.__circuit_breaker: AsyncCircuitBreaker = AsyncCircuitBreaker(
            FAILURE_THRESHOLD, RECOVERY_TIMEOUT, evaluate_error
        )

    async def start(self):
        if not self.__configurator.get("Crypto", "EnableUpdates", False):
            self.__log.info("[CryptoUpdater] Updates are disabled by configuration.")
            return

        self.__background_loop = AsyncLoop(self.__update_prices, UPDATE_INTERVAL, INITIAL_UPDATE_DELAY)
        self.__background_task = asyncio.create_task(self.__background_loop())
        self.__log.info(f"[CryptoUpdater] Started background task. {{ Delay = {INITIAL_UPDATE_DELAY}, Interval = {UPDATE_INTERVAL} }}")
        
    async def stop(self):
        loop = self.__background_loop
        if loop: loop.cancel()
        task = self.__background_task
        if task: await task
        self.__log.debug("[CryptoUpdater] Stopped background task.")
    
    # TODO Automatic detection of the addition/removal of a symbol.
    async def __update_prices(self):
        self.__log.debug("[CryptoUpdater] Updating prices...")
        try:
            prices = await self.__circuit_breaker(self.__get_symbol_prices)
            if len(prices) > 0:
                await self.__crypto_repository.update_prices(prices)
                self.__log.debug(f"[CryptoUpdater] Updated prices. {{ SymbolCount = {len(prices)} }}")
            else: self.__log.warning(f"[CryptoUpdater] Got no symbol data.")
        except (TooManyRequestsError, ImATeapotError) as error:
            self.__log.error(f"[CryptoUpdater] Update failed. {{ Reason = RateLimit, RetryIn = {self.__circuit_breaker.time_to_recover} }}", error)
        except HttpStatusError as error:
            self.__log.error(f"[CryptoUpdater] Update failed. {{ Reason = ServerError, RetryIn = {self.__circuit_breaker.time_to_recover} }}\n", error)
        except (ClientConnectionError, ClientConnectorError, ConnectionRefusedError, TimeoutError, AsyncIoTimeoutError) as error:
            self.__log.error(f"[CryptoUpdater] Update failed. {{ Reason = ConnectionError, RetryIn = {self.__circuit_breaker.time_to_recover} }}", error)
        except CircuitBrokenError:
            pass
        except Exception as error:
            self.__log.error(f"[CryptoUpdater] Update failed. Updates will stop. {{ Reason = UnexpectedError }}", error)
            raise

    async def __get_symbol_prices(self) -> List[PriceData]:
        result = await self.__http_client_pool.get(f"{BINANCE_API_BASE_URL}ticker/price")
        now = datetime.utcnow()
        return [PriceData(
            currency.get("symbol", ""),
            Decimal(currency.get("price", 0.0)),
            now
        ) for currency in result]
