from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.admin.enums import RuleState
from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class CommandRuleRecord(Record):
    id: PrimaryKey[int]
    created_at: datetime
    created_by: int
    server_id: int
    state: RuleState
    command_group: str | None
    command_subgroup: str | None
    command: str | None
    channel_id: int | None
