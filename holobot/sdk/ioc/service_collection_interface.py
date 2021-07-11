from .tservice import TService
from typing import Tuple, Type

class ServiceCollectionInterface:
    def get(self, type: Type[TService]) -> TService:
        raise NotImplementedError
    
    def get_all(self, type: Type[TService]) -> Tuple[TService, ...]:
        raise NotImplementedError
