from collections.abc import Sequence

from holobot.extensions.general.sdk.quests.models import QuestProtoId
from .iquest_event_handler import IQuestEventHandler

class QuestEventHandlerBase(IQuestEventHandler):
    @property
    def relevant_quests(self) -> Sequence[QuestProtoId]:
        return ()
