from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.extensions.dev.constants import DEV_FEATURE_NAME
from holobot.sdk.i18n import II18nManager, II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory, ILoggerManager
from holobot.sdk.logging.enums import LogLevel

@injectable(IWorkflow)
class ReloadI18nWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_manager: II18nManager,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        logger_manager: ILoggerManager
    ) -> None:
        super().__init__(
            required_permissions=Permission.ADMINISTRATOR
        )
        self.__i18n_manager = i18n_manager
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(ReloadI18nWorkflow)
        self.__logger_manager = logger_manager

    @command(
        description="Reloads the I18N file(s).",
        name="reloadi18n",
        group_name="dev",
        restrictions=(FeatureRestriction(feature_name=DEV_FEATURE_NAME),)
    )
    async def reload_i18n_files(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        self.__i18n_manager.reload_all()
        self.__logger.info("Reloaded I18N files")

        return self._reply(
            content=self.__i18n_provider.get(
                "extensions.dev.reload_i18n_workflow.reloaded_files"
            )
        )
