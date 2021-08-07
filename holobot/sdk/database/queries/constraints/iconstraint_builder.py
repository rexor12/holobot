from typing import Any, Tuple

class IConstraintBuilder:
    def build(self, base_param_index: int) -> Tuple[str, Tuple[Any, ...]]:
        raise NotImplementedError
