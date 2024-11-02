from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.extensions.dev.constants import DEV_FEATURE_NAME
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory, ILoggerManager
from holobot.sdk.logging.enums import LogLevel

@injectable(IWorkflow)
class SetLogLevelWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        logger_manager: ILoggerManager
    ) -> None:
        super().__init__(
            required_permissions=Permission.ADMINISTRATOR
        )
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(SetLogLevelWorkflow)
        self.__logger_manager = logger_manager

    @command(
        description="Sets the log level of the application.",
        name="setloglevel",
        group_name="dev",
        options=(
            Option("log_level", "The new log level.", OptionType.INTEGER, choices=(
                Choice("Trace", LogLevel.TRACE.value),
                Choice("Debug", LogLevel.DEBUG.value),
                Choice("Information", LogLevel.INFORMATION),
                Choice("Warning", LogLevel.WARNING),
                Choice("Error", LogLevel.ERROR),
                Choice("Critical", LogLevel.CRITICAL)
            )),
        ),
        restrictions=(FeatureRestriction(feature_name=DEV_FEATURE_NAME),)
    )
    async def set_maintenance_mode(
        self,
        context: InteractionContext,
        log_level: int
    ) -> InteractionResponse:
        self.__logger_manager.set_min_log_level(LogLevel(log_level))
        self.__logger.info("Changed log level", new_log_level=log_level)
        return self._reply(
            content=self.__i18n_provider.get(
                "extensions.dev.set_log_level_workflow.log_level_changed"
            )
        )
