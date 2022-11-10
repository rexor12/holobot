from holobot.extensions.dev.models import FeatureState
from holobot.sdk.database import IDatabaseManager
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .ifeature_sate_repository import IFeatureStateRepository
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
    def table_name(self) -> str:
        return "feature_states"

    def __init__(self, database_manager: IDatabaseManager) -> None:
        super().__init__(database_manager)

    def _map_record_to_model(self, record: FeatureStateRecord) -> FeatureState:
        return FeatureState(
            identifier=record.id,
            is_enabled=record.is_enabled
        )

    def _map_model_to_record(self, model: FeatureState) -> FeatureStateRecord:
        return FeatureStateRecord(
            id=model.identifier,
            is_enabled=model.is_enabled
        )
