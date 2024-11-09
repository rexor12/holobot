from holobot.extensions.mudada.models import HalloweenReward
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .ihalloween_reward_repository import IHalloweenRewardRepository
from .records import HalloweenRewardRecord

@injectable(IHalloweenRewardRepository)
class HalloweenRewardRepository(
    RepositoryBase[int, HalloweenRewardRecord, HalloweenReward],
    IHalloweenRewardRepository
):
    @property
    def record_type(self) -> type[HalloweenRewardRecord]:
        return HalloweenRewardRecord

    @property
    def model_type(self) -> type[HalloweenReward]:
        return HalloweenReward

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "mudada_halloween_rewards"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def _map_record_to_model(self, record: HalloweenRewardRecord) -> HalloweenReward:
        return HalloweenReward(
            identifier=record.id.value,
            last_update_at=record.last_update_at,
            last_reward_tier=record.last_reward_tier,
            is_tricked=record.is_tricked
        )

    def _map_model_to_record(self, model: HalloweenReward) -> HalloweenRewardRecord:
        return HalloweenRewardRecord(
            id=PrimaryKey(model.identifier),
            last_update_at=model.last_update_at,
            last_reward_tier=model.last_reward_tier,
            is_tricked=model.is_tricked
        )
