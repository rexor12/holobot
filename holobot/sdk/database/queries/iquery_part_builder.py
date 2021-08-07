from typing import Any, Tuple

class IQueryPartBuilder:
    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        raise NotImplementedError
