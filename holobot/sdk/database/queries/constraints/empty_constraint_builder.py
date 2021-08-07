from .iconstraint_builder import IConstraintBuilder
from typing import Any, Tuple

class EmptyConstraintBuilder(IConstraintBuilder):
    def build(self, base_param_index: int) -> Tuple[str, Tuple[Any, ...]]:
        return ("", ())
