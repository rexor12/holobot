from typing import Any, Protocol

class IConstraintBuilder(Protocol):
    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        ...
