from holobot.extensions.general.models.user_profiles import ReputationCooldown
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .ireputation_cooldown_repository import IReputationCooldownRepository
from .records import ReputationCooldownRecord

@injectable(IReputationCooldownRepository)
class ReputationCooldownRepository(
    RepositoryBase[str, ReputationCooldownRecord, ReputationCooldown],
    IReputationCooldownRepository
):
    @property
    def record_type(self) -> type[ReputationCooldownRecord]:
        return ReputationCooldownRecord

    @property
    def model_type(self) -> type[ReputationCooldown]:
        return ReputationCooldown

    @property
    def identifier_type(self) -> type[str]:
        return str

    @property
    def table_name(self) -> str:
        return "reputation_cooldowns"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def _map_record_to_model(self, record: ReputationCooldownRecord) -> ReputationCooldown:
        return ReputationCooldown(
            identifier=record.id.value,
            last_rep_at=record.last_rep_at,
            last_target_user_id=record.last_target_user_id
        )

    def _map_model_to_record(self, model: ReputationCooldown) -> ReputationCooldownRecord:
        return ReputationCooldownRecord(
            id=PrimaryKey(model.identifier),
            last_rep_at=model.last_rep_at,
            last_target_user_id=model.last_target_user_id
        )
