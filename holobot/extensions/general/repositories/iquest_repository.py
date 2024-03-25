from typing import Protocol

from holobot.extensions.general.models import Quest
from holobot.extensions.general.sdk.quests.models import QuestId
from holobot.sdk.database.repositories import IRepository

class IQuestRepository(
    IRepository[QuestId, Quest],
    Protocol
):
    pass
