from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

from .identifier import Identifier

TIdentifier = TypeVar("TIdentifier", bound=int | str | Identifier)

@dataclass(kw_only=True)
class AggregateRoot(ABC, Generic[TIdentifier]):
    """Abstract base class for an aggregate root."""

    identifier: TIdentifier
    """The identifier of the entity."""
