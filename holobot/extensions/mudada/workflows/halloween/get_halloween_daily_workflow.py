from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.models.embed import Embed, EmbedFooter
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentStyle, StackLayout
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.sdk.quests.enums import QuestStatus
from holobot.extensions.general.sdk.quests.exceptions import (
    InvalidQuestException, QuestOnCooldownException, QuestUnavailableException
)
from holobot.extensions.general.sdk.quests.managers import IQuestManager
from holobot.extensions.general.sdk.quests.models import CurrencyQuestReward, QuestProtoId
from holobot.extensions.mudada.constants import MUDADA_FEATURE_NAME
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.dict_utils import get_generic
from holobot.sdk.utils.iterable_utils import first, of_type

_QUEST_CODE = "MUDADA_HALLOWEEN_2024"

@injectable(IWorkflow)
class GetHalloweenDailyWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        member_data_provider: IMemberDataProvider,
        quest_manager: IQuestManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__logger = logger_factory.create(GetHalloweenDailyWorkflow)
        self.__member_data_provider = member_data_provider
        self.__quest_manager = quest_manager
        self.__unit_of_work_provider = unit_of_work_provider

    @command(
        group_name="mudada",
        subgroup_name="halloween",
        name="daily",
        description="Get your daily pumpkin.",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),)
    )
    async def get_halloween_daily_reward(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        quest_proto_id = QuestProtoId(server_id=context.server_id, code=_QUEST_CODE)
        quest_status = await self.__quest_manager.get_quest_status(
            context.server_id,
            context.author_id,
            quest_proto_id
        )
        if quest_status == QuestStatus.ON_COOLDOWN:
            return self._reply(content=self.__i18n.get(
                "extensions.mudada.get_halloween_daily_workflow.quest_on_cooldown_error"
            ))
        elif quest_status != QuestStatus.AVAILABLE:
            return self._reply(content=self.__i18n.get(
                "extensions.mudada.get_halloween_daily_workflow.quest_unavailable_error"
            ))

        return self._reply(
            content=self.__i18n.get("extensions.mudada.get_halloween_daily_workflow.choose_roll_message"),
            components=StackLayout(
                id="dummy",
                children=[
                    Button(
                        id="mdd_hallow_pkin",
                        owner_id=context.author_id,
                        style=ComponentStyle.SECONDARY,
                        emoji=1299389613877760071
                    )
                    for _ in range(5)
                ]
            )
        )

    @component(
        identifier="mdd_hallow_pkin",
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE,
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),)
    )
    async def claim_all_gifts(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                embed=None,
                components=None
            )

        member = await self.__member_data_provider.get_basic_data_by_id(context.server_id, context.author_id)
        if not member:
            return self._edit_message(
                content=self.__i18n.get("user_not_found_error"),
                embed=None,
                components=None
            )

        quest_proto_id = QuestProtoId(server_id=context.server_id, code=_QUEST_CODE)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            try:
                await self.__quest_manager.start_quest(context.server_id, context.author_id, quest_proto_id)
                rewards = await self.__quest_manager.complete_quest(context.server_id, context.author_id, quest_proto_id)
                currency = first(of_type(rewards.granted_items, CurrencyQuestReward))
                reward_tier = get_generic(currency.extension_data, int, "tier") or 0
                is_tricked = get_generic(currency.extension_data, bool, "is_tricked") or False

                unit_of_work.complete()

                if is_tricked:
                    return self._edit_message(
                        content=None,
                        embed=Embed(
                            title=self.__i18n.get(
                                "extensions.mudada.get_halloween_daily_workflow.trick_title"
                            ),
                            description=self.__i18n.get(
                                "extensions.mudada.get_halloween_daily_workflow.trick_message"
                            ),
                            image_url=self.__i18n.get_random_list_item(
                                "extensions.mudada.get_halloween_daily_workflow.trick_images"
                            ),
                            color=member.color,
                            footer=EmbedFooter(
                                text=self.__i18n.get(
                                    "extensions.mudada.get_halloween_daily_workflow.embed_footer"
                                )
                            )
                        ),
                        components=None
                    )

                return self._edit_message(
                    content=None,
                    embed=Embed(
                        title=self.__i18n.get(
                            "extensions.mudada.get_halloween_daily_workflow.treat_title"
                        ),
                        description=self.__i18n.get_list_item(
                            "extensions.mudada.get_halloween_daily_workflow.treat_messages",
                            reward_tier,
                            {
                                "emoji_id": currency.emoji_id,
                                "emoji_name": currency.emoji_name,
                                "amount": currency.count
                            }
                        ),
                        image_url=self.__i18n.get_random_list_item(
                            "extensions.mudada.get_halloween_daily_workflow.treat_images"
                        ),
                        color=member.color,
                        footer=EmbedFooter(
                            text=self.__i18n.get(
                                "extensions.mudada.get_halloween_daily_workflow.embed_footer"
                            )
                        )
                    ),
                    components=None
                )
            except InvalidQuestException:
                return self._edit_message(
                    content=self.__i18n.get("extensions.mudada.get_halloween_daily_workflow.invalid_quest_error"),
                    embed=None,
                    components=None
                )
            except QuestOnCooldownException:
                return self._edit_message(
                    content=self.__i18n.get("extensions.mudada.get_halloween_daily_workflow.quest_on_cooldown_error"),
                    embed=None,
                    components=None
                )
            except QuestUnavailableException:
                return self._edit_message(
                    content=self.__i18n.get("extensions.mudada.get_halloween_daily_workflow.quest_unavailable_error"),
                    embed=None,
                    components=None
                )