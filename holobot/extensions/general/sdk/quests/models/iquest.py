from datetime import datetime
from typing import Protocol

from .quest_id import QuestId

class IQuest(Protocol):
    """Represents a quest that is either in progress or completed by a character."""

    identifier: QuestId
    """The identifier of the quest."""

    completed_at: datetime
    """The date and time at which the quest was completed."""

    objective_count_1: int
    """The objective tracker for the first objective."""

    objective_count_2: int
    """The objective tracker for the second objective."""
