from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions.feature_restriction import (
    FeatureRestriction
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.sdk.quests.exceptions import (
    InvalidQuestException, QuestOnCooldownException, QuestUnavailableException
)
from holobot.extensions.general.sdk.quests.managers import IQuestManager
from holobot.extensions.general.sdk.quests.models import CurrencyQuestReward, QuestProtoId
from holobot.extensions.mudada.constants import (
    MUDADA_FEATURE_NAME, SUMMER_2024_DAILY_EVENT_TOGGLE_FEATURE_NAME
)
from holobot.extensions.mudada.workflows.decorators import requires_event
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.datetime_utils import utcnow
from holobot.sdk.utils.iterable_utils import first, of_type

_QUEST_CODE = "MUDADA_SUMMER_2024_DAILY"

@injectable(IWorkflow)
class GetSummerDailyWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        quest_manager: IQuestManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__logger = logger_factory.create(GetSummerDailyWorkflow)
        self.__quest_manager = quest_manager
        self.__unit_of_work_provider = unit_of_work_provider

    @requires_event(SUMMER_2024_DAILY_EVENT_TOGGLE_FEATURE_NAME)
    @command(
        group_name="mudada",
        subgroup_name="summer",
        name="daily",
        description="Gives you daily rewards during the Mudada Summer Beach Episode event.",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),)
    )
    async def get_summer_daily(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        quest_proto_id = QuestProtoId(server_id=context.server_id, code=_QUEST_CODE)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            try:
                await self.__quest_manager.start_quest(context.server_id, context.author_id, quest_proto_id)
                rewards = await self.__quest_manager.complete_quest(context.server_id, context.author_id, quest_proto_id)
                currency = first(of_type(rewards.granted_items, CurrencyQuestReward))

                unit_of_work.complete()

                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.get_summer_daily_workflow.quest_complete",
                        {
                            "emoji_id": currency.emoji_id,
                            "emoji_name": currency.emoji_name,
                            "amount": currency.count
                        }
                    )
                )
            except InvalidQuestException:
                # TODO Log only once every few mins/hours.
                self.__logger.error("An invalid daily reward quest ID is configured.")
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.get_summer_daily_workflow.invalid_quest_id"
                    )
                )
            except QuestOnCooldownException as error:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.get_summer_daily_workflow.cooldown_error",
                        {
                            "reset_at": int((utcnow() + error.time_left).timestamp())
                        }
                    )
                )
            except QuestUnavailableException:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.get_summer_daily_workflow.invalid_quest_id"
                    )
                )
