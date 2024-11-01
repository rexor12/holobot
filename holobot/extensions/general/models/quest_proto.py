from dataclasses import dataclass
from datetime import datetime, timedelta

from holobot.extensions.general.enums import QuestResetType
from holobot.extensions.general.sdk.quests.models import QuestProtoId
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class QuestProto(AggregateRoot[QuestProtoId]):
    reset_type: QuestResetType = QuestResetType.NONE
    reset_time: timedelta | None = None

    is_hidden: bool = False
    """Whether the quest should be hidden from the list of quests.

    Generally, this is useful when a quest has a dedicated UI
    or auto-completes in the background.
    """

    objective_type_1: int | None = None
    objective_target_1: int | None = None
    objective_count_1: int = 0
    objective_type_2: int | None = None
    objective_target_2: int | None = None
    objective_count_2: int = 0
    reward_xp: int = 0
    reward_sp: int = 0
    reward_item_id_1: int | None = None
    reward_item_count_1: int = 0
    reward_item_id_2: int | None = None
    reward_item_count_2: int = 0
    reward_item_id_3: int | None = None
    reward_item_count_3: int = 0
    reward_currency_id_1: int | None = None
    reward_currency_count_1: int
    reward_currency_id_2: int | None = None
    reward_currency_count_2: int
    reward_badge_sid_1: str | None
    reward_badge_id_1: int | None

    title: str | None = None
    """An optional title for the quest."""

    note: str | None = None
    """An optional note for the quest that is displayed in the embed footer."""

    completion_text: str | None = None
    """An optional text that is displayed as part of the quest completion."""

    valid_from: datetime | None = None
    """An optional date-time from which the quest is available (inclusive)."""

    valid_to: datetime | None = None
    """An optional date-time until which the quest is available (inclusive)."""
