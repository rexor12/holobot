from typing import Protocol, TypeVar

T = TypeVar("T", contravariant=True)

class ComparableProtocol(Protocol[T]):
    def __lt__(self, x: T) -> bool: ...

    def __gt__(self, x: T) -> bool: ...
