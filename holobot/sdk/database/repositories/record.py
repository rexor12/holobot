from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

TIdentifier = TypeVar("TIdentifier", int, str)

@dataclass(kw_only=True)
class Record(ABC, Generic[TIdentifier]):
    """Represents a record of a database table."""

    # NOTE By convention, only simple primary keys are supported
    # and they must be named as "id".
    id: TIdentifier
    """The identifier of the record."""
