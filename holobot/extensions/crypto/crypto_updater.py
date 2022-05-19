from .models import PriceData
from .repositories import CryptoRepositoryInterface
from aiohttp.client_exceptions import ClientConnectionError, ClientConnectorError
from asyncio.exceptions import TimeoutError as AsyncIoTimeoutError
from asyncio.tasks import Task
from datetime import datetime
from decimal import Decimal
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, ImATeapotError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreaker
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from typing import Awaitable, List, Optional

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
    def __init__(self,
        http_client_pool: HttpClientPoolInterface,
        crypto_repository: CryptoRepositoryInterface,
        configurator: ConfiguratorInterface,
        log: LogInterface):
        self.__http_client_pool: HttpClientPoolInterface = http_client_pool
        self.__crypto_repository: CryptoRepositoryInterface = crypto_repository
        self.__configurator: ConfiguratorInterface = configurator
        self.__log: LogInterface = log.with_name("Crypto", "CryptoUpdater")
        self.__token_source: Optional[CancellationTokenSource] = None
        self.__background_task: Optional[Awaitable[None]] = None
        self.__circuit_breaker: AsyncCircuitBreaker = AsyncCircuitBreaker(
            FAILURE_THRESHOLD, RECOVERY_TIMEOUT, evaluate_error
        )

    async def start(self):
        if not self.__configurator.get("Crypto", "EnableUpdates", False):
            self.__log.info("Updates are disabled by configuration.")
            return

        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__update_prices(self.__token_source.token)
        )
        self.__log.info(f"Started background task. {{ Delay = {INITIAL_UPDATE_DELAY}, Interval = {UPDATE_INTERVAL} }}")
        
    async def stop(self):
        if self.__token_source: self.__token_source.cancel()
        if self.__background_task:
            try:
                await self.__background_task
            except asyncio.exceptions.CancelledError:
                pass
        self.__log.debug("Stopped background task.")
    
    # TODO Automatic detection of the addition/removal of a symbol.
    async def __update_prices(self, token: CancellationToken) -> None:
        await wait(INITIAL_UPDATE_DELAY, token)
        while not token.is_cancellation_requested:
            self.__log.debug("Updating prices...")
            try:
                prices = await self.__circuit_breaker(self.__get_symbol_prices)
                if len(prices) > 0:
                    await self.__crypto_repository.update_prices(prices)
                    self.__log.debug(f"Updated prices. {{ SymbolCount = {len(prices)} }}")
                else: self.__log.warning(f"Got no symbol data.")
            except (TooManyRequestsError, ImATeapotError) as error:
                self.__log.error(f"Update failed. {{ Reason = RateLimit, RetryIn = {self.__circuit_breaker.time_to_recover} }}", error)
            except HttpStatusError as error:
                self.__log.error(f"Update failed. {{ Reason = ServerError, RetryIn = {self.__circuit_breaker.time_to_recover} }}\n", error)
            except (ClientConnectionError, ClientConnectorError, ConnectionRefusedError, ConnectionResetError, TimeoutError, AsyncIoTimeoutError) as error:
                self.__log.error(f"Update failed. {{ Reason = ConnectionError, RetryIn = {self.__circuit_breaker.time_to_recover} }}", error)
            except CircuitBrokenError:
                pass
            except Exception as error:
                self.__log.error(f"Update failed. Updates will stop. {{ Reason = UnexpectedError }}", error)
                raise
            await wait(UPDATE_INTERVAL, token)

    async def __get_symbol_prices(self) -> List[PriceData]:
        result = await self.__http_client_pool.get(f"{BINANCE_API_BASE_URL}ticker/price")
        now = datetime.utcnow()
        return [PriceData(
            currency.get("symbol", ""),
            Decimal(currency.get("price", 0.0)),
            now
        ) for currency in result]
