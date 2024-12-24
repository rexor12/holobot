from collections.abc import Sequence
from typing import Protocol

from holobot.extensions.general.sdk.quests.models import QuestProtoId

class IQuestEventHandler(Protocol):
    """Interface for a quest event handler."""

    @property
    def relevant_quests(self) -> Sequence[QuestProtoId]:
        """Gets a list of quest prototype identifiers
        that this handler can handle events for.

        Note: It is recommended to return a `set` here for improved performance.

        :return: The list of relevant quest prototype identifiers.
        :rtype: Sequence[QuestProtoId]
        """
        ...
