from aiohttp import ClientSession
from aiohttp.client import ClientTimeout
from aiohttp.client_reqrep import ClientResponse
from aiohttp.web_exceptions import HTTPForbidden, HTTPNotFound
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.logging.log_interface import LogInterface
from holobot.network.exceptions.http_status_error import HttpStatusError
from holobot.network.exceptions.im_a_teapot_error import ImATeapotError
from holobot.network.exceptions.too_many_requests_error import TooManyRequestsError
from holobot.network.http_client_pool_interface import HttpClientPoolInterface
from typing import Any, Callable, Dict

DEFAULT_TIMEOUT = ClientTimeout(total=5)

# https://julien.danjou.info/python-and-fast-http-clients/
class HttpClientPool(HttpClientPoolInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__error_map: Dict[int, Callable[[ClientResponse], Exception]] = {
            403: lambda _: HTTPForbidden(),
            404: lambda _: HTTPNotFound(),
            ImATeapotError.STATUS_CODE: ImATeapotError.from_client_response,
            TooManyRequestsError.STATUS_CODE: TooManyRequestsError.from_client_response
        }
        self.__session: ClientSession = ClientSession()
        self.__log = service_collection.get(LogInterface)

    async def close(self):
        self.__log.debug("[HttpClientPool] Closing session...")
        await self.__session.close()
        self.__log.debug("[HttpClientPool] Successfully closed session.")

    async def get(self, url: str, query_parameters: Dict[str, str] = None):
        async with self.__session.get(url, params=query_parameters, timeout=DEFAULT_TIMEOUT) as response:
            self.__raise_on_error(response)
            return await response.json()
    
    async def post(self, url: str, json: Dict[str, Any]):
        async with self.__session.post(url, json=json, timeout=DEFAULT_TIMEOUT) as response:
            self.__raise_on_error(response)
            return await response.json()
    
    def __raise_on_error(self, response: ClientResponse):
        if (error_factory := self.__error_map.get(response.status, None)):
            raise error_factory(response)
        if 400 <= response.status <= 599:
            raise HttpStatusError(response.status)