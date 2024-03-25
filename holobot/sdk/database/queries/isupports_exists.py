from typing import Protocol

from .exists_builder import ExistsBuilder

class ISupportsExists(Protocol):
    def exists(self) -> ExistsBuilder:
        ...
