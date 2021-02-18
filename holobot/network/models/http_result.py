from aiohttp.client_reqrep import ClientResponse
from typing import Any, Dict

HTTP_STATUS_OK = 200

class HttpResult:
    def __init__(self, response: ClientResponse):
        self.is_success: bool = response.status == HTTP_STATUS_OK
        self.status_code: int = response.status
        self.__response: ClientResponse = response
    
    async def read_json(self) -> Dict[str, Any]:
        return await self.__response.json()