from holobot.extensions.mudada.models import FeatureState
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .ifeature_state_repository import IFeatureStateRepository
from .records import FeatureStateRecord

@injectable(IFeatureStateRepository)
class FeatureStateRepository(
    RepositoryBase[str, FeatureStateRecord, FeatureState],
    IFeatureStateRepository
):
    @property
    def record_type(self) -> type[FeatureStateRecord]:
        return FeatureStateRecord

    @property
    def model_type(self) -> type[FeatureState]:
        return FeatureState

    @property
    def identifier_type(self) -> type[str]:
        return str

    @property
    def table_name(self) -> str:
        return "mudada_feature_states"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def _map_record_to_model(self, record: FeatureStateRecord) -> FeatureState:
        return FeatureState(
            identifier=record.id.value,
            is_enabled=record.is_enabled
        )

    def _map_model_to_record(self, model: FeatureState) -> FeatureStateRecord:
        return FeatureStateRecord(
            id=PrimaryKey(model.identifier),
            is_enabled=model.is_enabled
        )
