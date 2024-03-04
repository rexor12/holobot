from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(kw_only=True)
class Identifier(ABC):
    """Represents the identifier of a database entity."""

    @abstractmethod
    def __str__(self) -> str:
        """Gets a string representation of the identifier that is also equally unique.

        This may be used in constructs such as a unit of work.
        """
        raise NotImplementedError
