from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.options import EconomicOptions
from holobot.extensions.general.sdk.quests.exceptions import (
    InvalidQuestException, QuestOnCooldownException, QuestUnavailableException
)
from holobot.extensions.general.sdk.quests.managers import IQuestManager
from holobot.extensions.general.sdk.quests.models import QuestProtoId
from holobot.extensions.general.utils.workflow_utils import create_quest_reward_embed
from holobot.sdk.configs import IOptions
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.timedelta_utils import textify_timedelta

@injectable(IWorkflow)
class GetDailyRewardWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        options: IOptions[EconomicOptions],
        quest_manager: IQuestManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__logger = logger_factory.create(GetDailyRewardWorkflow)
        self.__options = options
        self.__quest_manager = quest_manager
        self.__unit_of_work_provider = unit_of_work_provider

    @command(
        group_name="economic",
        name="daily",
        description="Get your daily reward chest."
    )
    async def get_daily_reward(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        if not self.__options.value.DailyCheckInQuestCode:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.get_daily_reward_workflow.daily_reward_disabled"
                )
            )

        quest_proto_id = QuestProtoId(server_id="0", code=self.__options.value.DailyCheckInQuestCode)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            try:
                await self.__quest_manager.start_quest("0", context.author_id, quest_proto_id)
                rewards = await self.__quest_manager.complete_quest("0", context.author_id, quest_proto_id)

                unit_of_work.complete()

                return self._reply(
                    embed=create_quest_reward_embed(self.__i18n, rewards, self.__options.value)
                )
            except InvalidQuestException:
                # TODO Log only once every few mins/hours.
                self.__logger.error("An invalid daily reward quest ID is configured.")
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.get_daily_reward_workflow.invalid_quest_id"
                    )
                )
            except QuestOnCooldownException as error:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.get_daily_reward_workflow.cooldown_error",
                        {
                            "cooldown": textify_timedelta(error.time_left)
                        }
                    )
                )
            except QuestUnavailableException:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.get_daily_reward_workflow.invalid_quest_id"
                    )
                )
