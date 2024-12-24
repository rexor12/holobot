from collections.abc import Awaitable

from holobot.extensions.general.sdk.quests.models import IQuest
from .iquest_event_handler import IQuestEventHandler

class IQuestCompleteEventHandler(IQuestEventHandler):
    """Interface for a quest event handler that is invoked
    when a user successfully completes a quest.
    """

    def on_quest_complete(
        self,
        quest: IQuest,
        server_id: int,
        user_id: int
    ) -> Awaitable[None]:
        ...
