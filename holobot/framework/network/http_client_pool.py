from aiohttp import ClientSession
from aiohttp.client import ClientTimeout
from aiohttp.web_exceptions import HTTPError, HTTPForbidden, HTTPNotFound
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.network import HttpClientPoolInterface
from holobot.sdk.network.exceptions import HttpStatusError, ImATeapotError, TooManyRequestsError
from multidict import CIMultiDict
from typing import Any, Callable, Dict

DEFAULT_TIMEOUT = ClientTimeout(total=5)

# https://julien.danjou.info/python-and-fast-http-clients/
@injectable(StartableInterface)
@injectable(HttpClientPoolInterface)
class HttpClientPool(HttpClientPoolInterface, StartableInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__error_map: Dict[int, Callable[[CIMultiDict], Exception]] = {
            403: lambda _: HTTPForbidden(),
            404: lambda _: HTTPNotFound(),
            ImATeapotError.STATUS_CODE: ImATeapotError.from_headers,
            TooManyRequestsError.STATUS_CODE: TooManyRequestsError.from_headers
        }
        self.__session: ClientSession = ClientSession()
        self.__log = service_collection.get(LogInterface).with_name("Framework", "HttpClientPool")

    async def stop(self):
        self.__log.debug("Closing session...")
        await self.__session.close()
        self.__log.debug("Successfully closed session.")

    async def get(self, url: str, query_parameters: Dict[str, Any] = None) -> Any:
        try:
            async with self.__session.get(url, params=query_parameters, timeout=DEFAULT_TIMEOUT) as response:
                return await response.json()
        except HTTPError as error:
            self.__raise_on_error(error)
    
    async def post(self, url: str, json: Dict[str, Any]) -> Any:
        try:
            async with self.__session.post(url, json=json, timeout=DEFAULT_TIMEOUT) as response:
                return await response.json()
        except HTTPError as error:
            self.__raise_on_error(error)
    
    def __raise_on_error(self, error: HTTPError):
        if (error_factory := self.__error_map.get(error.status, None)):
            raise error_factory(error.headers)
        raise HttpStatusError(error.status)
