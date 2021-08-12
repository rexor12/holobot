from datetime import timedelta
from typing import Generic, TypeVar

T = TypeVar("T", int, float, timedelta)

class Range(Generic[T]):
    def __init__(self, lower_bound: T, upper_bound: T) -> None:
        super().__init__()
        self.__lower_bound: T = lower_bound
        self.__upper_bound: T = upper_bound
    
    @property
    def lower_bound(self) -> T:
        return self.__lower_bound
    
    @property
    def upper_bound(self) -> T:
        return self.__upper_bound

    def __contains__(self, key: T) -> bool:
        return self.lower_bound <= key <= self.upper_bound
