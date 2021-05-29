from typing import Any, List, Type

class ServiceProviderBase:
    def knows(self, intf: Type[Any]) -> bool:
        impls = self.get_impls(intf)
        return impls is not None and len(impls) > 0

    def get_impls(self, intf: Type[Any]) -> List[Type]:
        raise NotImplementedError
