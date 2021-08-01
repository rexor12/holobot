from .iconstraint_builder import IConstraintBuilder
from ..enums import Equality
from typing import Any, Optional, Tuple

class ColumnConstraintBuilder(IConstraintBuilder):
    def __init__(self, column_name: str, equality: Equality, value: Optional[Any]) -> None:
        self.__column_name: str = column_name
        self.__equality: Equality = equality
        self.__value: Optional[Any] = value
    
    @property
    def column_name(self) -> str:
        return self.__column_name
    
    @property
    def equality(self) -> Equality:
        return self.__equality
    
    @property
    def value(self) -> Optional[Any]:
        return self.__value

    def build(self, base_param_index: int) -> Tuple[str, Tuple[Any, ...]]:
        sql = [self.column_name]
        arguments = []
        if self.value is None:
            sql.append("IS NULL")
        elif self.__equality == Equality.EQUAL:
            sql.append("=")
            sql.append(f"${base_param_index}")
            arguments.append(self.value)
        return (" ".join(sql), tuple(arguments))

def column_expression(column_name: str, equality: Equality, value: Optional[Any]) -> ColumnConstraintBuilder:
    return ColumnConstraintBuilder(column_name, equality, value)
