from holobot.dependency_injection.providers.service_provider_base import ServiceProviderBase
from typing import Any, Dict, List, Type, TypeVar

_T = TypeVar("_T")

class SimpleServiceProvider(ServiceProviderBase):
    def __init__(self):
        self.__impls: Dict[Type[Any], List[Type[Any]]] = {}

    def register(self, intf: Type[_T], impl: Type[Any]):
        if not (impls := self.__impls.get(intf, None)):
            self.__impls[intf] = impls = []
        if not impl in impls:
            impls.append(impl)
    
    def get_impls(self, intf: Type[_T]) -> List[Type[Any]]:
        return self.__impls.get(intf, [])