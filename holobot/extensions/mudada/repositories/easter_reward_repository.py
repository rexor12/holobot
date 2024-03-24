from holobot.extensions.mudada.models import EasterReward
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .ieaster_reward_repository import IEasterRewardRepository
from .records import EasterRewardRecord

@injectable(IEasterRewardRepository)
class EasterRewardRepository(
    RepositoryBase[str, EasterRewardRecord, EasterReward],
    IEasterRewardRepository
):
    @property
    def record_type(self) -> type[EasterRewardRecord]:
        return EasterRewardRecord

    @property
    def model_type(self) -> type[EasterReward]:
        return EasterReward

    @property
    def identifier_type(self) -> type[str]:
        return str

    @property
    def table_name(self) -> str:
        return "mudada_easter_rewards"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def _map_record_to_model(self, record: EasterRewardRecord) -> EasterReward:
        return EasterReward(
            identifier=record.id.value,
            last_update_at=record.last_update_at,
            last_reward_tier=record.last_reward_tier
        )

    def _map_model_to_record(self, model: EasterReward) -> EasterRewardRecord:
        return EasterRewardRecord(
            id=PrimaryKey(model.identifier),
            last_update_at=model.last_update_at,
            last_reward_tier=model.last_reward_tier
        )
