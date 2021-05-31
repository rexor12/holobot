from .service_provider_base import ServiceProviderBase
from typing import Any, Dict, List, Type

class SimpleServiceProvider(ServiceProviderBase):
    def __init__(self) -> None:
        self.__impls: Dict[Type[Any], List[Type[Any]]] = {}

    def register(self, intf: Type[Any], impl: Type[Any]) -> None:
        if not (impls := self.__impls.get(intf, None)):
            self.__impls[intf] = impls = []
        if not impl in impls:
            impls.append(impl)
    
    def get_impls(self, intf: Type[Any]) -> List[Type[Any]]:
        return self.__impls.get(intf, [])
