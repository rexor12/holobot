from typing import Protocol, TypeVar

from .iquery_part_builder import IQueryPartBuilder

TCompiledQuery = TypeVar("TCompiledQuery", covariant=True)

class ICompileableQueryPartBuilder(IQueryPartBuilder, Protocol[TCompiledQuery]):
    def compile(self) -> TCompiledQuery:
        ...
