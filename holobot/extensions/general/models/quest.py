from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.general.sdk.quests.models import IQuest, QuestId
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class Quest(AggregateRoot[QuestId], IQuest):
    """Represents a quest that is either in progress or completed by a character."""

    completed_at: datetime | None = None
    """The date and time at which the quest was completed."""

    objective_count_1: int = 0
    """The objective tracker for the first objective."""

    objective_count_2: int = 0
    """The objective tracker for the second objective."""
