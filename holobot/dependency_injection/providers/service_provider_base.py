from typing import List, Type, TypeVar

_T = TypeVar("_T")

class ServiceProviderBase:
    def knows(self, intf: Type[_T]) -> bool:
        impls = self.get_impls(intf)
        return impls is not None and len(impls) > 0

    def get_impls(self, intf: Type[_T]) -> List[Type]:
        raise NotImplementedError