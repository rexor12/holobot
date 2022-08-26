from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

TIdentifier = TypeVar("TIdentifier")

@dataclass(kw_only=True)
class Entity(ABC, Generic[TIdentifier]):
    # NOTE By convention, only simple primary keys are supported
    # and they must be named as "id".
    id: TIdentifier
