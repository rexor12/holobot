from typing import Any

class IQueryPartBuilder:
    def build(self) -> tuple[str, tuple[Any, ...]]:
        raise NotImplementedError
