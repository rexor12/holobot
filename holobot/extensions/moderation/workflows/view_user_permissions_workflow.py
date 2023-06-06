from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import ServerNotFoundError, UserNotFoundError
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.servers.models import MemberData
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComboBox, ComboBoxItem, ComponentBase, LayoutBase, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.models import ComboBoxState, PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.extensions.moderation.models import User
from holobot.extensions.moderation.repositories import IUserRepository
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import paginate_with_fallback
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

_DEFAULT_PAGE_SIZE = 10

@injectable(IWorkflow)
class ViewUserPermissionsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        user_repository: IUserRepository
    ) -> None:
        super().__init__(
            required_permissions=Permission.ADMINISTRATOR
        )
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__user_repository = user_repository

    @command(
        name="view",
        group_name="moderation",
        subgroup_name="permissions",
        description="Displays a specific user's moderator permissions or a list of moderators.",
        options=(
            Option("user", "The user to view.", type=OptionType.USER, is_mandatory=False),
        ),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def view_permissions(
        self,
        context: InteractionContext,
        user: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        return (
            await self.__view_user_permissions(context, str(user))
            if user else await self.__view_moderators(context)
        )

    @component(identifier="modpermspagi")
    async def change_page(
        self,
        context: InteractionContext,
        state: PagerState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__create_page_content(
            context.server_id,
            state.owner_id,
            state.current_page,
            _DEFAULT_PAGE_SIZE,
            0
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(identifier="modpermscb")
    async def change_user(
        self,
        context: InteractionContext,
        state: ComboBoxState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        page_index, user_index = state.selected_values[0].split(";")
        content, embed, components = await self.__create_page_content(
            context.server_id,
            state.owner_id,
            max(int(page_index), 0),
            _DEFAULT_PAGE_SIZE,
            max(int(user_index), 0)
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __view_user_permissions(
        self,
        context: ServerChatInteractionContext,
        user_id: str
    ) -> InteractionResponse:
        user = await self.__try_get_moderator_user(context.server_id, user_id)
        return (
            self._reply(
                embed=self.__create_embed(
                    user,
                    await self.__try_get_user_data(context.server_id, user.user_id)
                )
            )
            if user
            else self._reply(
                content=self.__i18n_provider.get("user_not_found_error")
            )
        )

    async def __view_moderators(
        self,
        context: ServerChatInteractionContext,
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page_content(
            context.server_id,
            context.author_id,
            0,
            _DEFAULT_PAGE_SIZE,
            0
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed = embed if isinstance(embed, Embed) else None,
            components=components
        )

    async def __create_page_content(
        self,
        server_id: str,
        owner_id: str,
        page_index: int,
        page_size: int,
        user_index: int
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        pagination = await paginate_with_fallback(
            lambda pindex, psize, sid: self.__user_repository.get_moderators(sid, pindex, psize),
            page_index,
            page_size,
            server_id
        )
        if not pagination.items:
            return (
                self.__i18n_provider.get(
                    "extensions.moderation.view_user_permissions_workflow.no_moderators_error"
                ),
                None,
                None
            )

        user_index = min(user_index, len(pagination.items) - 1)
        current_member_data = await self.__try_get_user_data(
            server_id,
            pagination.items[user_index].user_id
        )
        combo_box_items = list[ComboBoxItem]()
        for index, user in enumerate(pagination.items):
            member_data = await self.__try_get_user_data(
                server_id,
                user.user_id
            )
            combo_box_items.append(
                ComboBoxItem(
                    text=self.__i18n_provider.get(
                        "extensions.moderation.view_user_permissions_workflow.user_with_name"
                        if member_data
                        else "extensions.moderation.view_user_permissions_workflow.user_without_name",
                        {
                            "user_name": member_data and member_data.display_name,
                            "user_id": user.user_id
                        }
                    ),
                    value=f"{pagination.page_index};{index}"
                )
            )

        return (
            None,
            self.__create_embed(pagination.items[user_index], current_member_data),
            [
                StackLayout(id="modperms1", children=[
                    ComboBox(
                        id="modpermscb",
                        owner_id=owner_id,
                        placeholder=self.__i18n_provider.get(
                            "extensions.moderation.view_user_permissions_workflow.embed_placeholder"
                        ),
                        items=combo_box_items
                    )
                ]),
                Paginator(
                    id="modpermspagi",
                    owner_id=owner_id,
                    current_page=pagination.page_index,
                    page_size=pagination.page_size,
                    total_count=pagination.total_count
                )
            ]
        )

    def __create_embed(
        self,
        user: User,
        member_data: MemberData | None
    ) -> Embed:
        embed = Embed(
            title=self.__i18n_provider.get(
                "extensions.moderation.view_user_permissions_workflow.embed_title"
            ),
            description=self.__i18n_provider.get(
                "extensions.moderation.view_user_permissions_workflow.embed_description",
                { "user_id": user.user_id }
            ),
            thumbnail_url=(
                member_data
                and (member_data.server_specific_avatar_url or member_data.avatar_url)
            )
        )

        for permission in ModeratorPermission:
            if permission is ModeratorPermission.NONE:
                continue

            embed.fields.append(EmbedField(
                name=self.__i18n_provider.get(
                    f"extensions.moderation.permissions.{permission.value}"
                ),
                value=self.__i18n_provider.get(
                    "extensions.moderation.view_user_permissions_workflow.has_permission"
                    if permission in user.permissions
                    else "extensions.moderation.view_user_permissions_workflow.not_has_permission"
                )
            ))

        return embed

    async def __try_get_user_data(
        self,
        server_id: str,
        user_id: str
    ) -> MemberData | None:
        try:
            user_data = await self.__member_data_provider.get_basic_data_by_id(
                server_id,
                user_id
            )
            return user_data
        except (ServerNotFoundError, UserNotFoundError):
            return None

    async def __try_get_moderator_user(
        self,
        server_id: str,
        user_id: str
    ) -> User | None:
        try:
            return await self.__user_repository.get_by_server(server_id, user_id)
        except (ServerNotFoundError, UserNotFoundError):
            return None
