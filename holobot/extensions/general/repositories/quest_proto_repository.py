from holobot.extensions.general.enums import QuestResetType
from holobot.extensions.general.models import QuestProto
from holobot.extensions.general.sdk.quests.models import QuestProtoId
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iquest_proto_repository import IQuestProtoRepository
from .records import QuestProtoRecord

@injectable(IQuestProtoRepository)
class QuestProtoRepository(
    RepositoryBase[QuestProtoId, QuestProtoRecord, QuestProto],
    IQuestProtoRepository
):
    @property
    def record_type(self) -> type[QuestProtoRecord]:
        return QuestProtoRecord

    @property
    def model_type(self) -> type[QuestProto]:
        return QuestProto

    @property
    def identifier_type(self) -> type[QuestProtoId]:
        return QuestProtoId

    @property
    def table_name(self) -> str:
        return "quest_protos"

    def _map_record_to_model(self, record: QuestProtoRecord) -> QuestProto:
        return QuestProto(
            identifier=QuestProtoId(
                server_id=record.server_id.value,
                code=record.code.value
            ),
            reset_type=QuestResetType(record.reset_type),
            reset_time=record.reset_time,
            is_hidden=record.is_hidden,
            objective_type_1=record.objective_type_1,
            objective_target_1=record.objective_target_1,
            objective_count_1=record.objective_count_1,
            objective_type_2=record.objective_type_2,
            objective_target_2=record.objective_target_2,
            objective_count_2=record.objective_count_2,
            reward_xp=record.reward_xp,
            reward_sp=record.reward_sp,
            reward_item_id_1=record.reward_item_id_1,
            reward_item_count_1=record.reward_item_count_1,
            reward_item_id_2=record.reward_item_id_2,
            reward_item_count_2=record.reward_item_count_2,
            reward_item_id_3=record.reward_item_id_3,
            reward_item_count_3=record.reward_item_count_3,
            reward_currency_id_1=record.reward_currency_id_1,
            reward_currency_count_1=record.reward_currency_count_1,
            reward_currency_id_2=record.reward_currency_id_2,
            reward_currency_count_2=record.reward_currency_count_2,
            reward_badge_sid_1=record.reward_badge_sid_1,
            reward_badge_id_1=record.reward_badge_id_1,
            title=record.title,
            note=record.note,
            completion_text=record.completion_text,
            valid_from=record.valid_from,
            valid_to=record.valid_to
        )

    def _map_model_to_record(self, model: QuestProto) -> QuestProtoRecord:
        return QuestProtoRecord(
            server_id=PrimaryKey(model.identifier.server_id),
            code=PrimaryKey(model.identifier.code),
            reset_type=model.reset_type.value,
            reset_time=model.reset_time,
            is_hidden=model.is_hidden,
            objective_type_1=model.objective_type_1,
            objective_target_1=model.objective_target_1,
            objective_count_1=model.objective_count_1,
            objective_type_2=model.objective_type_2,
            objective_target_2=model.objective_target_2,
            objective_count_2=model.objective_count_2,
            reward_xp=model.reward_xp,
            reward_sp=model.reward_sp,
            reward_item_id_1=model.reward_item_id_1,
            reward_item_count_1=model.reward_item_count_1,
            reward_item_id_2=model.reward_item_id_2,
            reward_item_count_2=model.reward_item_count_2,
            reward_item_id_3=model.reward_item_id_3,
            reward_item_count_3=model.reward_item_count_3,
            reward_currency_id_1=model.reward_currency_id_1,
            reward_currency_count_1=model.reward_currency_count_1,
            reward_currency_id_2=model.reward_currency_id_2,
            reward_currency_count_2=model.reward_currency_count_2,
            reward_badge_sid_1=model.reward_badge_sid_1,
            reward_badge_id_1=model.reward_badge_id_1,
            title=model.title,
            note=model.note,
            completion_text=model.completion_text,
            valid_from=model.valid_from,
            valid_to=model.valid_to
        )
