from holobot.extensions.general.models import Quest
from holobot.extensions.general.sdk.quests.models import QuestId
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iquest_repository import IQuestRepository
from .records import QuestRecord

@injectable(IQuestRepository)
class QuestRepository(
    RepositoryBase[QuestId, QuestRecord, Quest],
    IQuestRepository
):
    @property
    def record_type(self) -> type[QuestRecord]:
        return QuestRecord

    @property
    def model_type(self) -> type[Quest]:
        return Quest

    @property
    def identifier_type(self) -> type[QuestId]:
        return QuestId

    @property
    def table_name(self) -> str:
        return "quests"

    def _map_record_to_model(self, record: QuestRecord) -> Quest:
        return Quest(
            identifier=QuestId(
                server_id=record.server_id.value,
                user_id=record.user_id.value,
                quest_proto_code=record.quest_proto_code.value
            ),
            completed_at=record.completed_at,
            objective_count_1=record.objective_count_1,
            objective_count_2=record.objective_count_2
        )

    def _map_model_to_record(self, model: Quest) -> QuestRecord:
        return QuestRecord(
            server_id=PrimaryKey(model.identifier.server_id),
            user_id=PrimaryKey(model.identifier.user_id),
            quest_proto_code=PrimaryKey(model.identifier.quest_proto_code),
            completed_at=model.completed_at,
            objective_count_1=model.objective_count_1,
            objective_count_2=model.objective_count_2
        )
