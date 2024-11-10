from collections.abc import Sequence
from typing import Protocol

from holobot.sdk.database.migration.models import MigrationPlan

class IMigration(Protocol):
    @property
    def table_name(self) -> str:
        ...

    @property
    def plans(self) -> Sequence[MigrationPlan]:
        ...
