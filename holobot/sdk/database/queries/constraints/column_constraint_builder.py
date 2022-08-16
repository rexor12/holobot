from typing import Any

from ..enums import Equality
from .iconstraint_builder import IConstraintBuilder

class ColumnConstraintBuilder(IConstraintBuilder):
    def __init__(self, column_name: str, equality: Equality, value: Any | None, is_raw_value: bool = False) -> None:
        self.__column_name: str = column_name
        self.__equality: Equality = equality
        self.__value: Any | None = value
        self.__is_raw_value: bool = is_raw_value

    @property
    def column_name(self) -> str:
        return self.__column_name

    @property
    def equality(self) -> Equality:
        return self.__equality

    @property
    def value(self) -> Any | None:
        return self.__value

    @property
    def is_raw_value(self) -> bool:
        return self.__is_raw_value

    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        sql = [self.column_name]
        arguments = []
        if self.value is None:
            sql.append("IS NULL")
        else:
            sql.append(self.equality.to_operator())
            if self.is_raw_value:
                sql.append(self.value)
            else:
                sql.append(f"${base_param_index}")
                arguments.append(self.value)
        return (" ".join(sql), tuple(arguments))

def column_expression(
    column_name: str,
    equality: Equality,
    value: Any | None,
    is_raw_value: bool = False
) -> ColumnConstraintBuilder:
    return ColumnConstraintBuilder(column_name, equality, value, is_raw_value)
