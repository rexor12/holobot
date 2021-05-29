from typing import Any, Dict

# NOTE: The HTTP methods return the JSON responses.
class HttpClientPoolInterface:
    async def close(self):
        pass

    async def get(self, url: str, query_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        raise NotImplementedError
    
    async def post(self, url: str, json: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
