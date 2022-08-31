from __future__ import annotations

from typing import Any

from .compiled_query import CompiledQuery
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder

class OnConflictUpdateBuilder(ICompileableQueryPartBuilder[CompiledQuery]):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__table_name: str = ""
        self.__fields: dict[str, tuple[Any | None, bool]] = {}

    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def set_fields(self) -> dict[str, Any | None]:
        return self.__fields

    def field(self, column_name: str, value: Any | None, is_raw_value: bool = False) -> OnConflictUpdateBuilder:
        self.__fields[column_name] = (value, is_raw_value)
        return self

    def fields(self, field: tuple[str, Any | None], *fields: tuple[str, Any | None]) -> OnConflictUpdateBuilder:
        self.__fields[field[0]] = (field[1], False)
        for f in fields:
            self.__fields[f[0]] = (f[1], False)
        return self

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        if not self.__fields:
            raise ValueError("The UPDATE clause must have at least one field.")

        parent_sql, parent_args = self.__parent_builder.build()
        sql = [parent_sql, "UPDATE", self.__table_name, "SET"]
        arguments = list(parent_args)
        if len(self.__fields) > 1:
            sql.extend(("(", ", ".join(self.__fields), ") = ("))
            is_first_value = True
            index = 1
            for value, is_raw_value in self.__fields.values():
                if not is_first_value:
                    sql.append(", ")
                if is_raw_value:
                    sql.append(str(value))
                else:
                    sql.append(f"${len(parent_args) + index}")
                    arguments.append(value)
                    index += 1
                is_first_value = False
            sql.append(")")
        else:
            column, value = next(iter(self.__fields.items()))
            sql.extend((column, "="))
            if value[1]:
                sql.append(str(value[0]))
            else:
                sql.append(f"${len(parent_args) + 1}")
                arguments.append(value[0])

        return (" ".join(sql), tuple(arguments))
