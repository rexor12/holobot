from .iconstraint_builder import IConstraintBuilder
from typing import Any

class EmptyConstraintBuilder(IConstraintBuilder):
    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        return ("", ())
