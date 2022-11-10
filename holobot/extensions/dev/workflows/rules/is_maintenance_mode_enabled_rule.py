from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Command, Interactable
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.extensions.dev.managers import IMaintenanceManager
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflowExecutionRule)
class IsMaintenanceModeEnabledRule(IWorkflowExecutionRule):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        maintenance_manager: IMaintenanceManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__maintenance_manager = maintenance_manager

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> tuple[bool, str | None]:
        if isinstance(interactable, Command) and interactable.group_name == "dev":
            return (False, None)

        return (
            await self.__maintenance_manager.is_maintenance_mode_enabled(),
            self.__i18n_provider.get("extensions.dev.maintenance_mode_enabled_error")
        )
