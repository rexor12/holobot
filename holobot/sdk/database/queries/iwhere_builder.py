from typing import Protocol

from .compiled_query import CompiledQuery
from .constraints import IConstraintBuilder
from .icompileable_query_part_builder import ICompileableQueryPartBuilder

class IWhereBuilder(ICompileableQueryPartBuilder[CompiledQuery], Protocol):
    @property
    def constraint(self) -> IConstraintBuilder:
        ...

    @constraint.setter
    def constraint(self, value: IConstraintBuilder) -> None:
        ...
