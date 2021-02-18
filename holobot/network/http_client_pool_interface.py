from typing import Any, Dict

class HttpClientPoolInterface:
    async def close(self):
        pass

    async def get(self, url: str, query_parameters: Dict[str, str] = None):
        raise NotImplementedError
    
    async def post(self, url: str, json: Dict[str, Any]):
        raise NotImplementedError