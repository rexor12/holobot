from typing import Any, Literal

from .compiled_query import CompiledQuery
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder
from .where_builder import WhereBuilder

JOIN_TYPE = Literal["LEFT", "RIGHT", "INNER", "OUTER", "FULL OUTER"]

class JoinBuilder(ICompileableQueryPartBuilder[CompiledQuery]):
    def __init__(
        self,
        parent_builder: IQueryPartBuilder,
        table_name: str,
        left_column: str,
        right_column: str,
        alias: str | None = None,
        join_type: JOIN_TYPE = "LEFT"
    ) -> None:
        super().__init__()
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__table_name: str = table_name
        self.__left_column: str = left_column
        self.__right_column: str = right_column
        self.__alias: str | None = alias
        self.__join_type: JOIN_TYPE = join_type

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)

    def build(self) -> tuple[str, tuple[Any, ...]]:
        parent_sql = self.__parent_builder.build()
        base_index = len(parent_sql[1])
        sql = [parent_sql[0], f"{self.__join_type} JOIN {self.__table_name}"]
        if self.__alias:
            sql.append(f"AS {self.__alias}")
        sql.append("ON")
        sql.append(self.__left_column)
        sql.append("=")
        sql.append(self.__right_column)

        return (" ".join(sql), parent_sql[1])
