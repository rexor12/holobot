from typing import Protocol

from holobot.extensions.general.models import QuestProto
from holobot.extensions.general.sdk.quests.models import QuestProtoId
from holobot.sdk.database.repositories import IRepository

class IQuestProtoRepository(
    IRepository[QuestProtoId, QuestProto],
    Protocol
):
    pass
