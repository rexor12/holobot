from typing import Any

from .iconstraint_builder import IConstraintBuilder

class ColumnLikeConstraintBuilder(IConstraintBuilder):
    def __init__(
        self,
        column_name: str,
        value: str,
        is_case_insensitive: bool
    ) -> None:
        self.__column_name = column_name
        self.__value = value
        self.__is_case_insensitive = is_case_insensitive

    @property
    def column_name(self) -> str:
        return self.__column_name

    @property
    def value(self) -> str:
        return self.__value

    @property
    def is_case_insensitive(self) -> bool:
        return self.__is_case_insensitive

    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        sql = [
            self.column_name,
            "ILIKE" if self.is_case_insensitive else "LIKE",
            f"${base_param_index}"
        ]

        return (" ".join(sql), tuple([self.__value]))

def column_like_expression(
    column_name: str,
    value: str,
    is_case_insensitive: bool
) -> ColumnLikeConstraintBuilder:
    return ColumnLikeConstraintBuilder(column_name, value, is_case_insensitive)
