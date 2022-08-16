from typing import Any

class IConstraintBuilder:
    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        raise NotImplementedError
