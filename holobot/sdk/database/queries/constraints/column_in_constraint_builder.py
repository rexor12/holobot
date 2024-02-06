from collections.abc import Sequence
from typing import Any

from holobot.sdk.exceptions import ArgumentError
from .iconstraint_builder import IConstraintBuilder

class ColumnInConstraintBuilder(IConstraintBuilder):
    def __init__(
        self,
        column_name: str,
        values: Sequence[Any]
    ) -> None:
        if len(values) == 0:
            raise ArgumentError("values", "At least one value must be specified.")

        self.__column_name = column_name
        self.__values = values

    @property
    def column_name(self) -> str:
        return self.__column_name

    @property
    def value(self) -> Sequence[Any]:
        return self.__values

    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        # TODO Figure out what to cast to.
        sql = [self.column_name, "=", f"any(${base_param_index}::bigint[])"]
        return (" ".join(sql), tuple([self.value]))
