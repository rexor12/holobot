from holobot.extensions.mudada.models import UserReward
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iuser_reward_repository import IUserRewardRepository
from .records import UserRewardRecord

@injectable(IUserRewardRepository)
class UserRewardRepository(
    RepositoryBase[int, UserRewardRecord, UserReward],
    IUserRewardRepository
):
    @property
    def record_type(self) -> type[UserRewardRecord]:
        return UserRewardRecord

    @property
    def model_type(self) -> type[UserReward]:
        return UserReward

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "user_rewards"

    @property
    def schema_name(self) -> str:
        return "mudada"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def _map_record_to_model(self, record: UserRewardRecord) -> UserReward:
        return UserReward(
            identifier=record.id.value,
            reward_amount=record.reward_amount
        )

    def _map_model_to_record(self, model: UserReward) -> UserRewardRecord:
        return UserRewardRecord(
            id=PrimaryKey(model.identifier),
            reward_amount=model.reward_amount
        )
