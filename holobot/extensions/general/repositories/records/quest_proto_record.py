from dataclasses import dataclass
from datetime import timedelta

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class QuestProtoRecord(Record):
    server_id: PrimaryKey[str]
    code: PrimaryKey[str]
    reset_type: int
    reset_time: timedelta | None
    is_hidden: bool
    objective_type_1: int | None
    objective_target_1: int | None
    objective_count_1: int
    objective_type_2: int | None
    objective_target_2: int | None
    objective_count_2: int
    reward_xp: int
    reward_sp: int
    reward_item_id_1: int | None
    reward_item_count_1: int
    reward_item_id_2: int | None
    reward_item_count_2: int
    reward_item_id_3: int | None
    reward_item_count_3: int
    reward_currency_id_1: int | None
    reward_currency_count_1: int
    reward_currency_id_2: int | None
    reward_currency_count_2: int
    reward_badge_sid_1: str | None
    reward_badge_id_1: int | None
    title: str | None
    note: str | None
    completion_text: str | None
