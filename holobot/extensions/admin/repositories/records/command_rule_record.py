from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.admin.enums import RuleState
from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class CommandRuleRecord(Entity[int]):
    id: int
    created_at: datetime
    created_by: str
    server_id: str
    state: RuleState
    command_group: str | None
    command_subgroup: str | None
    command: str | None
    channel_id: str | None
