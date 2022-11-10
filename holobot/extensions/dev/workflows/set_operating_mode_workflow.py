from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.extensions.dev.managers import IMaintenanceManager
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

_NORMAL_MODE = 0
_MAINTENANCE_MODE =1

@injectable(IWorkflow)
class SetOperatingModeWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        maintenance_manager: IMaintenanceManager
    ) -> None:
        super().__init__(
            required_permissions=Permission.ADMINISTRATOR
        )
        self.__i18n_provider = i18n_provider
        self.__maintenance_manager = maintenance_manager

    @command(
        description="Sets the operating mode of the application.",
        name="setmode",
        group_name="dev",
        options=(
            Option("mode", "The new operating mode", OptionType.INTEGER, choices=(
                Choice("Normal", _NORMAL_MODE),
                Choice("Maintenance", _MAINTENANCE_MODE)
            )),
        ),
        # TODO Provide development server ID dynamically. (#135)
        server_ids={"999259836439081030"}
    )
    async def set_maintenance_mode(
        self,
        context: InteractionContext,
        mode: int
    ) -> InteractionResponse:
        await self.__maintenance_manager.set_maintenance_mode(mode == _MAINTENANCE_MODE)
        return self._reply(
            content=self.__i18n_provider.get(
                "extensions.dev.set_operating_mode_workflow.maintenance_mode_enabled"
                if mode == 1
                else "extensions.dev.set_operating_mode_workflow.normal_mode_enabled"
            )
        )
