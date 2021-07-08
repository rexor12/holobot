from .deferred_service import DeferredService
from .tservice import TService
from typing import Tuple, Type

class ServiceCollectionInterface:
    async def close(self):
        pass

    def get(self, type: Type[TService]) -> TService:
        raise NotImplementedError
    
    def get_all(self, type: Type[TService]) -> Tuple[TService, ...]:
        raise NotImplementedError
    
    def get_deferred(self, type: Type[TService]) -> DeferredService[TService]:
        raise NotImplementedError
