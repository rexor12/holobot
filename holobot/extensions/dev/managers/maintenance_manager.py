from holobot.extensions.dev.models import FeatureState
from holobot.extensions.dev.repositories import IFeatureStateRepository
from holobot.sdk.ioc.decorators import injectable
from .imaintenance_manager import IMaintenanceManager

@injectable(IMaintenanceManager)
class MaintenanceManager(IMaintenanceManager):
    _FEATURE_NAME = "MaintenanceMode"

    def __init__(
        self,
        feature_state_repository: IFeatureStateRepository
    ) -> None:
        super().__init__()
        self.__feature_state_repository = feature_state_repository

    async def is_maintenance_mode_enabled(self) -> bool:
        feature_state = await self.__feature_state_repository.get(MaintenanceManager._FEATURE_NAME)
        return feature_state.is_enabled if feature_state else False

    async def set_maintenance_mode(self, is_enabled: bool) -> None:
        feature_state = await self.__feature_state_repository.get(MaintenanceManager._FEATURE_NAME)
        if feature_state:
            feature_state.is_enabled = is_enabled
            await self.__feature_state_repository.update(feature_state)
            return

        await self.__feature_state_repository.add(FeatureState(
            identifier=MaintenanceManager._FEATURE_NAME,
            is_enabled=is_enabled
        ))
