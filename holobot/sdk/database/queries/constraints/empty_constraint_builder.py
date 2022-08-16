from typing import Any

from .iconstraint_builder import IConstraintBuilder

class EmptyConstraintBuilder(IConstraintBuilder):
    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        return ("", ())
