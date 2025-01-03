from typing import cast

from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentBase, ComponentStyle, LayoutBase, Paginator, PaginatorState,
    StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.extensions.general.managers.user_profiles import IUserProfileManager
from holobot.extensions.general.models.items import BadgeItem
from holobot.extensions.general.models.user_profiles import UserProfile
from holobot.extensions.general.repositories import IBadgeRepository, IUserItemRepository
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.iterable_utils import batch
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

_BADGE_SERVER_ID_PARAMETER: str = "s"
_BADGE_ID_PARAMETER: str = "b"
_SLOT_INDEX_PARAMETER: str = "i"

@injectable(IWorkflow)
class ViewUserBadgesWorkflow(WorkflowBase):
    _DEFAULT_PAGE_SIZE = 5

    def __init__(
        self,
        badge_repository: IBadgeRepository,
        i18n_provider: II18nProvider,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_data_provider: IUserDataProvider,
        user_item_repository: IUserItemRepository,
        user_profile_repository: IUserProfileRepository,
        user_profile_manager: IUserProfileManager
    ) -> None:
        super().__init__()
        self.__badge_repository = badge_repository
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_data_provider = user_data_provider
        self.__user_item_repository = user_item_repository
        self.__user_profile_repository = user_profile_repository
        self.__user_profile_manager = user_profile_manager

    @command(
        group_name="profile",
        name="badges",
        description="Displays a user's badges.",
        cooldown=Cooldown(duration=5),
        options=(
            Option("user", "An optional user to view.", OptionType.USER, False),
        )
    )
    async def view_user_badges(
        self,
        context: InteractionContext,
        user: int | None = None
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page_content(
            context.author_id,
            0,
            ViewUserBadgesWorkflow._DEFAULT_PAGE_SIZE,
            user if user else context.author_id
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @component(
        identifier="ubadgepagi",
        is_bound=True
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if not (user_id := get_custom_int(state.custom_data, "u")):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                embed=None,
                components=None
            )

        content, embed, components = await self.__create_page_content(
            state.owner_id,
            max(state.current_page, 0),
            ViewUserBadgesWorkflow._DEFAULT_PAGE_SIZE,
            user_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="ubadgepagir",
        is_bound=True
    )
    async def change_to_first_page(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if not (user_id := get_custom_int(state.custom_data, "u")):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                embed=None,
                components=None
            )

        content, embed, components = await self.__create_page_content(
            state.owner_id,
            0,
            ViewUserBadgesWorkflow._DEFAULT_PAGE_SIZE,
            user_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="setbadge",
        is_bound=True
    )
    async def select_badge_slot_index(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            (badge_server_id := get_custom_int(state.custom_data, _BADGE_SERVER_ID_PARAMETER)) is None
            or (badge_id := get_custom_int(state.custom_data, _BADGE_ID_PARAMETER)) is None
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        badge = await self.__badge_repository.get(
            BadgeId(server_id=badge_server_id, badge_id=badge_id)
        )
        if not badge:
            return self._edit_message(
                content=self.__i18n.get(
                    "extensions.general.view_user_badges_workflow.invalid_badge_error"
                ),
                embed=None,
                components=None
            )

        layouts = list[LayoutBase]()
        for slot_indices in batch(range(UserProfile.MAX_BADGE_COUNT), 4):
            layouts.append(StackLayout(
                id="dummy",
                children=[
                    Button(
                        id="setbadgex",
                        owner_id=state.owner_id,
                        text=str(slot_index + 1),
                        style=ComponentStyle.SECONDARY,
                        custom_data={
                            _BADGE_SERVER_ID_PARAMETER: str(badge_server_id),
                            _BADGE_ID_PARAMETER: str(badge_id),
                            _SLOT_INDEX_PARAMETER: str(slot_index)
                        }
                    )
                    for slot_index in slot_indices
                ]
            ))
        layouts.append(StackLayout(
            id="dummy",
            children=[
                Button(
                    id="ubadgepagir",
                    owner_id=context.author_id,
                    text=self.__i18n.get(
                        "extensions.general.view_user_badges_workflow.equip_another_button"
                    ),
                    custom_data={
                        "u": str(context.author_id)
                    }
                )
            ]
        ))

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.general.view_user_badges_workflow.equip_position_confirmation",
                {
                    "emoji_name": badge.emoji_name,
                    "emoji_id": badge.emoji_id,
                    "badge_name": badge.name
                }
            ),
            embed=None,
            components=layouts
        )

    @component(
        identifier="setbadgex",
        is_bound=True
    )
    async def set_user_profile_badge(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            (badge_server_id := get_custom_int(state.custom_data, _BADGE_SERVER_ID_PARAMETER)) is None
            or (badge_id := get_custom_int(state.custom_data, _BADGE_ID_PARAMETER)) is None
            or (slot_index := get_custom_int(state.custom_data, _SLOT_INDEX_PARAMETER)) is None
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            typed_badge_id = BadgeId(server_id=badge_server_id, badge_id=badge_id)
            has_badge = await self.__user_item_repository.badge_exists(
                badge_server_id,
                context.author_id,
                badge_id
            )
            if (
                not has_badge
                or not (badge := await self.__badge_repository.get(typed_badge_id))
            ):
                return self._edit_message(
                    content=self.__i18n.get(
                        "extensions.general.view_user_badges_workflow.badge_not_owned_error"
                    ),
                    embed=None,
                    components=None
                )

            user_profile = await self.__user_profile_manager.get_or_create(context.author_id)
            user_profile.badges.remove_item(typed_badge_id)
            user_profile.badges.set_item(slot_index, typed_badge_id)
            await self.__user_profile_repository.update(user_profile)

            unit_of_work.complete()

            return self._edit_message(
                content=self.__i18n.get(
                    "extensions.general.view_user_badges_workflow.badges_updated",
                    {
                        "emoji_name": badge.emoji_name,
                        "emoji_id": badge.emoji_id,
                        "badge_name": badge.name,
                        "slot_index": str(slot_index + 1)
                    }
                ),
                embed=None,
                components=StackLayout(
                    id="dummy",
                    children=[
                        Button(
                            id="vprofile",
                            owner_id=context.author_id,
                            text=self.__i18n.get(
                                "extensions.general.view_user_badges_workflow.view_profile_button"
                            ),
                            custom_data={ "u": str(context.author_id) }
                        ),
                        Button(
                            id="ubadgepagir",
                            owner_id=context.author_id,
                            text=self.__i18n.get(
                                "extensions.general.view_user_badges_workflow.equip_another_button"
                            ),
                            custom_data={
                                "u": str(context.author_id)
                            }
                        )
                    ]
                )
            )

    async def __create_page_content(
        self,
        owner_id: int,
        page_index: int,
        page_size: int,
        user_id: int
    ) -> tuple[
        UndefinedOrNoneOr[str],
        UndefinedOrNoneOr[Embed],
        ComponentBase | list[LayoutBase] | None
    ]:
        is_self = owner_id == user_id
        result = await self.__user_item_repository.paginate_badges(user_id, page_index, page_size)
        if not result.items:
            return (
                self.__i18n.get(
                    "extensions.general.view_user_badges_workflow.no_user_badges_error"
                    if is_self
                    else "extensions.general.view_user_badges_workflow.no_other_user_badges_error",
                    {
                        "user_id": user_id
                    }
                ),
                None,
                None
            )

        badge_descriptors = list[str]()
        layouts = list[LayoutBase]()
        for user_items in batch(result.items, 5):
            layout = StackLayout(id="dummy")

            for user_item in user_items:
                badge_item = cast(BadgeItem, user_item.item)
                badge_id = BadgeId(
                    server_id=badge_item.badge_id.server_id,
                    badge_id=badge_item.badge_id.badge_id
                )
                badge = await self.__badge_repository.get(badge_id)
                if not badge:
                    continue

                is_equipped = await self.__user_profile_repository.is_badge_equipped(user_id, badge_id)
                badge_descriptors.append(self.__i18n.get(
                    (
                        "extensions.general.view_user_badges_workflow.badge_description_equipped"
                        if is_equipped
                        else "extensions.general.view_user_badges_workflow.badge_description"
                    ),
                    {
                        "emoji_name": badge.emoji_name,
                        "emoji_id": badge.emoji_id,
                        "name": badge.name,
                        "description": badge.description,
                        "unlocked_at": int(badge_item.unlocked_at.timestamp())
                    }
                ))

                if not is_self:
                    continue

                layout.children.append(Button(
                    id="setbadge",
                    owner_id=owner_id,
                    text=self.__i18n.get(
                        "extensions.general.view_user_badges_workflow.equip_button"
                    ),
                    style=ComponentStyle.SECONDARY,
                    emoji=badge.emoji_id,
                    custom_data={
                        _BADGE_SERVER_ID_PARAMETER: str(badge.identifier.server_id),
                        _BADGE_ID_PARAMETER: str(badge.identifier.badge_id)
                    }
                ))

            if is_self:
                layouts.append(layout)

        user_data = await self.__user_data_provider.get_user_data_by_id(user_id)
        embed = Embed(
            title=self.__i18n.get(
                "extensions.general.view_user_badges_workflow.embed_title",
                {
                    "username": user_data.name
                }
            ),
            description="\n\n".join(badge_descriptors),
            thumbnail_url=user_data.avatar_url
        )

        layouts.append(Paginator(
            id="ubadgepagi",
            owner_id=owner_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count,
            custom_data={ "u": user_id }
        ))

        return (None, embed, layouts)
