from collections.abc import Awaitable, Callable
from typing import Any

from aiohttp import ClientSession, TCPConnector
from aiohttp.client import ClientTimeout
from aiohttp.web_exceptions import HTTPError, HTTPForbidden, HTTPNotFound
from multidict import CIMultiDict

from holobot.framework.configs import EnvironmentOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.network.exceptions import HttpStatusError, ImATeapotError, TooManyRequestsError
from holobot.sdk.threading.utils import COMPLETED_TASK

DEFAULT_TIMEOUT = ClientTimeout(total=5)

@injectable(IStartable)
@injectable(IHttpClientPool)
class HttpClientPool(IHttpClientPool, IStartable):
    @property
    def priority(self) -> int:
        return 10

    def __init__(
        self,
        logger_factory: ILoggerFactory,
        options: IOptions[EnvironmentOptions]
    ) -> None:
        self.__options = options
        self.__error_map: dict[int, Callable[[CIMultiDict], Exception]] = {
            403: lambda _: HTTPForbidden(),
            404: lambda _: HTTPNotFound(),
            ImATeapotError.STATUS_CODE: ImATeapotError.from_headers,
            TooManyRequestsError.STATUS_CODE: TooManyRequestsError.from_headers
        }
        self.__session: ClientSession | None = None
        self.__logger = logger_factory.create(HttpClientPool)

    def start(self) -> Awaitable[None]:
        self.__session = ClientSession(
            connector=TCPConnector(limit=self.__options.value.HttpPoolSize)
        )
        return COMPLETED_TASK

    async def stop(self):
        self.__logger.debug("Closing session...")
        if self.__session:
            await self.__session.close()
        self.__logger.debug("Successfully closed session")

    async def get(self, url: str, query_parameters: dict[str, Any] | None = None) -> Any:
        assert self.__session
        try:
            async with self.__session.get(url, params=query_parameters, timeout=DEFAULT_TIMEOUT) as response:
                return await response.json()
        except HTTPError as error:
            self.__raise_on_error(error)

    async def get_raw(self, url: str, query_parameters: dict[str, Any] | None = None) -> bytes:
        assert self.__session
        try:
            async with self.__session.get(url, params=query_parameters, timeout=DEFAULT_TIMEOUT) as response:
                return await response.read()
        except HTTPError as error:
            self.__raise_on_error(error)
            raise Exception # Won't be hit

    async def post(self, url: str, json: dict[str, Any]) -> Any:
        assert self.__session
        try:
            async with self.__session.post(url, json=json, timeout=DEFAULT_TIMEOUT) as response:
                return await response.json()
        except HTTPError as error:
            self.__raise_on_error(error)

    def __raise_on_error(self, error: HTTPError):
        if (error_factory := self.__error_map.get(error.status)):
            raise error_factory(error.headers)
        raise HttpStatusError(error.status)
