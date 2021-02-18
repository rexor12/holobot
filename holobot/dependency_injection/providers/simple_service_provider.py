from holobot.dependency_injection.providers.service_provider_base import ServiceProviderBase
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from typing import Dict, List, Type, TypeVar

_T = TypeVar("_T")

class SimpleServiceProvider(ServiceProviderBase):
    def __init__(self):
        self.__impls: Dict[Type, List[Type]] = {}

    def register(self, intf: Type[_T], impl: Type):
        if (impls := self.__impls.get(intf, None)) is None:
            self.__impls[intf] = impls = []
        if not impl in impls:
            impls.append(impl)
    
    def get_impls(self, intf: Type[_T]) -> List[Type]:
        return self.__impls.get(intf, [])