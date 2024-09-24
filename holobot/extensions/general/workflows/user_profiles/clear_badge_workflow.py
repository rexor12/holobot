from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentBase, ComponentStyle, LayoutBase, Paginator, PaginatorState,
    StackLayout
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums.option_type import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.interactables.models.choice import Choice
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.managers.user_profiles import IUserProfileManager
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

_ALL_SLOTS: int = -1

@injectable(IWorkflow)
class ClearUserBadgeWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_profile_repository: IUserProfileRepository,
        user_profile_manager: IUserProfileManager
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_profile_repository = user_profile_repository
        self.__user_profile_manager = user_profile_manager

    @command(
        group_name="profile",
        name="clearbadge",
        description="Removes a badge from display on your user profile.",
        cooldown=Cooldown(duration=2),
        options=(
            Option(
                "slot",
                "The slot from which to remove the badge.",
                OptionType.INTEGER,
                True,
                choices=(
                    Choice("Slot 1", 0),
                    Choice("Slot 2", 1),
                    Choice("Slot 3", 2),
                    Choice("Slot 4", 3),
                    Choice("Slot 5", 4),
                    Choice("Slot 6", 5),
                    Choice("Slot 7", 6),
                    Choice("Slot 8", 7),
                    Choice("All slots", _ALL_SLOTS),
                )
            ),
        ),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def clear_badge(
        self,
        context: InteractionContext,
        slot: int
    ) -> InteractionResponse:
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            user_profile = await self.__user_profile_manager.get_or_create(context.author_id)
            if slot == _ALL_SLOTS:
                user_profile.badges.remove_all()
                i18n_key = "extensions.general.clear_badge_workflow.cleared_all_badges"
            else:
                user_profile.badges.remove_item(slot)
                i18n_key = "extensions.general.clear_badge_workflow.cleared_badge"

            await self.__user_profile_repository.update(user_profile)

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                i18n_key,
                { "slot_index" : (slot + 1) }
            ),
            components=StackLayout(
                id="dummy",
                children=[
                    Button(
                        id="vprofile",
                        owner_id=context.author_id,
                        text=self.__i18n.get(
                            "extensions.general.clear_badge_workflow.view_profile_button"
                        ),
                        custom_data={ "u": context.author_id }
                    ),
                    Button(
                        id="ubadgepagir",
                        owner_id=context.author_id,
                        text=self.__i18n.get(
                            "extensions.general.clear_badge_workflow.view_badges_button"
                        ),
                        custom_data={ "u": context.author_id }
                    )
                ]
            )
        )
