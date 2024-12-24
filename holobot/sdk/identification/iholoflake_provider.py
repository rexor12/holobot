from typing import Protocol

from .holoflake import Holoflake

class IHoloflakeProvider(Protocol):
    def get_next_id(self) -> Holoflake:
        ...
