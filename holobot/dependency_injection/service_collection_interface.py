from typing import List, Type, TypeVar

T = TypeVar("T")

class ServiceCollectionInterface:
    async def close(self):
        pass

    def get(self, type: Type[T]) -> T:
        raise NotImplementedError
    
    def get_all(self, type: Type[T]) -> List[T]:
        raise NotImplementedError