from typing import Any, Protocol

class IQueryPartBuilder(Protocol):
    def build(self) -> tuple[str, tuple[Any, ...]]:
        ...
