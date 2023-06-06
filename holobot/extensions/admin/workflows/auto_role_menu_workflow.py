from dataclasses import dataclass, field
from datetime import timedelta
from itertools import islice
from math import ceil
from typing import NamedTuple

from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ForbiddenError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentStyle, LayoutBase, RoleSelector, RoleSelectorState, StackLayout,
    TextBox, TextBoxState
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component, modal
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.interactables.views import Modal, ModalState
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.caching import IObjectCache, SlidingExpirationCacheEntryPolicy
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.iterable_utils import has_any
from holobot.sdk.utils.uuid_utils import random_uuid

_BUILDER_EXPIRATION_TIME = 5 * 60
_MAX_ROLE_COUNT = 15
_MAX_MENU_TITLE_LENGTH = 120
_MAX_MENU_DESCRIPTION_LENGTH = 120

class _RoleOptions(NamedTuple):
    role_id: str
    emoji_mention: str

@dataclass
class _AutoRoleMenuBuilder:
    id: str
    owner_id: str
    is_exclusive: bool
    show_roles: bool
    title: str
    description: str | None
    # role_id, emoji_id, emoji mention
    roles: list[_RoleOptions] = field(default_factory=list)
    current_role_id: str | None = None
    is_new: bool = True

@injectable(IWorkflow)
class AutoRoleMenuWorkflow(WorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        emoji_data_provider: IEmojiDataProvider,
        i18n_provider: II18nProvider,
        user_manager: IUserManager
    ) -> None:
        super().__init__()
        self.__cache = cache.get_view(str, _AutoRoleMenuBuilder)
        self.__emoji_data_provider = emoji_data_provider
        self.__i18n = i18n_provider
        self.__user_manager = user_manager

    @command(
        group_name="admin",
        subgroup_name="autorole",
        name="create",
        description="Create a new auto role menu in the current channel.",
        options=(
            Option("title", "The title of the role menu.", is_mandatory=True),
            Option("role", "The first self-assignable role.", OptionType.ROLE, True),
            Option("emoji", "The emoji to represent the role.", OptionType.STRING, True),
            Option("description", "An optional description of the menu.", OptionType.STRING, False),
            Option("exclusive", "Whether only one role can be selected.", OptionType.BOOLEAN, False),
            Option("show_roles", "Whether the roles should be displayed.", OptionType.BOOLEAN, False)
        ),
        cooldown=Cooldown(duration=60),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def create_auto_role_menu(
        self,
        context: InteractionContext,
        title: str,
        role: int,
        emoji: str,
        description: str | None = None,
        exclusive: bool = False,
        show_roles: bool = True
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        if (
            len(title) > _MAX_MENU_TITLE_LENGTH
            or (description and len(description) > _MAX_MENU_DESCRIPTION_LENGTH)
        ):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.details_too_long_error"),
                is_ephemeral=True
            )

        if (
            (emoji_data := await self.__emoji_data_provider.find_emoji(emoji.strip(), context.server_id)) is None
            or not emoji_data.identifier
            or not emoji_data.mention
        ):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.emoji_not_found_error"),
                is_ephemeral=True
            )

        builder = _AutoRoleMenuBuilder(
            random_uuid(8),
            context.author_id,
            exclusive,
            show_roles,
            title,
            description,
            [
                _RoleOptions(
                    str(role),
                    emoji_data.mention
                )
            ]
        )
        await self.__cache.add_or_replace(
            AutoRoleMenuWorkflow.__get_cache_key(context.server_id, builder.id),
            builder,
            SlidingExpirationCacheEntryPolicy(timedelta(seconds=_BUILDER_EXPIRATION_TIME))
        )

        embed, components = self.__create_view(builder, False)

        return self._reply(
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="armdel",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def delete_auto_role_menu(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (state_id := state.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        await self.__cache.remove(cache_key)

        return self._delete()

    @component(
        identifier="armhome",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def show_main_menu(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (state_id := state.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        embed, components = self.__create_view(builder, False)

        return self._edit_message(
            content=None,
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="armadd",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def show_new_role_selector(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (state_id := state.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        if len(builder.roles) >= _MAX_ROLE_COUNT:
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.too_many_roles_error"),
                is_ephemeral=True
            )

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.admin.auto_role_menu_workflow.role_selector_message"
            ),
            components=[
                StackLayout(
                    id="armrolesel",
                    children=[
                        RoleSelector(
                            id="armrolesel",
                            owner_id=state.owner_id,
                            custom_data={
                                "i": state_id
                            }
                        )
                    ]
                ),
                StackLayout(
                    id="armroleselb",
                    children=[
                        Button(
                            id="armhome",
                            owner_id=state.owner_id,
                            text="⬅️",
                            custom_data={
                                "i": state_id
                            }
                        )
                    ]
                )
            ]
        )

    @component(
        identifier="armrolesel",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def show_new_role_modal(
        self,
        context: InteractionContext,
        state: RoleSelectorState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (state_id := state.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        if len(builder.roles) >= _MAX_ROLE_COUNT:
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.too_many_roles_error"),
                is_ephemeral=True
            )

        role_id = state.selected_values[0]
        if has_any(builder.roles, lambda i: i.role_id == role_id):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.role_added_already_error"),
                is_ephemeral=True
            )

        builder.current_role_id = state.selected_values[0]

        return self._show_modal(
            modal=Modal(
                identifier="armaddm",
                owner_id=builder.owner_id,
                title=self.__i18n.get(
                    "extensions.admin.auto_role_menu_workflow.role_modal_title"
                ),
                components=[
                    TextBox(
                        id="tbemoji",
                        owner_id=state.owner_id,
                        label=self.__i18n.get(
                            "extensions.admin.auto_role_menu_workflow.role_modal_field"
                        ),
                        is_required=True,
                        min_length=1,
                        max_length=32,
                        custom_data={
                            "i": state_id
                        }
                    )
                ]
            )
        )

    @modal(
        identifier="armaddm",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def add_new_role(
        self,
        context: InteractionContext,
        state: ModalState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (tb_emoji := state.get_component_state(TextBoxState, "tbemoji"))
            or not tb_emoji.value
            or not (state_id := tb_emoji.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        if len(builder.roles) >= _MAX_ROLE_COUNT:
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.too_many_roles_error"),
                is_ephemeral=True
            )

        if (
            (emoji_data := await self.__emoji_data_provider.find_emoji(tb_emoji.value.strip(), context.server_id)) is None
            or not emoji_data.identifier
            or not emoji_data.mention
        ):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.emoji_not_found_error"),
                is_ephemeral=True
            )

        # NOTE: If for some reason the role ID isn't present,
        # we silently ignore it and navigate back.
        if builder.current_role_id:
            builder.roles.append(_RoleOptions(
                builder.current_role_id,
                emoji_data.mention
            ))

        embed, components = self.__create_view(builder, False)

        return self._edit_message(
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="armfin",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def finalize_auto_role_menu(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (state_id := state.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        await self.__cache.remove(cache_key)

        embed, components = self.__create_view(builder, True)

        return self._edit_message(
            content=None,
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="armgr",
        required_permissions=Permission.NONE
    )
    async def update_user_role(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (is_finalized := state.custom_data.get("f"))
            or not (role_id := state.custom_data.get("r"))
            or not (is_exclusive := state.custom_data.get("e"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        if is_finalized != "1":
            if context.author_id != state.owner_id:
                return self._reply(
                    content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_in_progress_error"),
                    is_ephemeral=True
                )

            return await self.__try_remove_role(context, state)

        try:
            if await self.__user_manager.has_role(context.server_id, context.author_id, role_id):
                await self.__user_manager.remove_role(
                    context.server_id,
                    context.author_id,
                    role_id
                )

                return self._reply(
                    content=self.__i18n.get(
                        "extensions.admin.auto_role_menu_workflow.user_role_removed",
                        {
                            "role_id": role_id
                        }
                    ),
                    is_ephemeral=True
                )

            if is_exclusive == "1":
                await self.__remove_exclusive_user_roles(context)

            await self.__user_manager.assign_role(
                context.server_id,
                context.author_id,
                role_id
            )

            return self._reply(
                content=self.__i18n.get(
                    "extensions.admin.auto_role_menu_workflow.user_role_added",
                    {
                        "role_id": role_id
                    }
                ),
                is_ephemeral=True
            )
        except ForbiddenError:
            return self._reply(
                content=self.__i18n.get("missing_dm_permission_error")
            )
        except UserNotFoundError:
            return self._reply(
                content=self.__i18n.get("user_not_found_error")
            )
        except ServerNotFoundError:
            return self._reply(
                content=self.__i18n.get("server_not_found_error")
            )
        except ChannelNotFoundError:
            return self._reply(
                content=self.__i18n.get("channel_not_found_error")
            )

    @component(
        identifier="armedit",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def edit_auto_role_menu(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not context.message
            or not context.message.embeds
            or not (is_exclusive := state.custom_data.get("e"))
            or not (show_roles := state.custom_data.get("r"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        embed = context.message.embeds[0]
        builder = _AutoRoleMenuBuilder(
            random_uuid(8),
            context.author_id,
            is_exclusive == "1",
            show_roles == "1",
            embed.title or "Auto Role Menu",
            embed.description,
            [
                _RoleOptions(
                    role_id,
                    component.emoji.mention
                )
                for component in context.message.components
                if (
                    component.identifier == "armgr"
                    and isinstance(component, ButtonState)
                    and (role_id := component.custom_data.get("r"))
                    and component.emoji
                    and component.emoji.mention
                )
            ],
            is_new=False
        )
        await self.__cache.add_or_replace(
            AutoRoleMenuWorkflow.__get_cache_key(context.server_id, builder.id),
            builder,
            SlidingExpirationCacheEntryPolicy(timedelta(seconds=_BUILDER_EXPIRATION_TIME))
        )

        embed, components = self.__create_view(builder, False)

        return self._edit_message(
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="armeditdetail",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def show_auto_role_menu_detail_modal(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (state_id := state.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        return self._show_modal(
            modal=Modal(
                identifier="armdetailm",
                owner_id=builder.owner_id,
                title=self.__i18n.get(
                    "extensions.admin.auto_role_menu_workflow.detail_modal_title"
                ),
                components=[
                    TextBox(
                        id="tbtitle",
                        owner_id=state.owner_id,
                        label=self.__i18n.get(
                            "extensions.admin.auto_role_menu_workflow.detail_modal_title_field"
                        ),
                        default_value=builder.title,
                        is_required=True,
                        min_length=1,
                        max_length=_MAX_MENU_TITLE_LENGTH,
                        custom_data={
                            "i": state_id
                        }
                    ),
                    TextBox(
                        id="tbdescription",
                        owner_id=state.owner_id,
                        label=self.__i18n.get(
                            "extensions.admin.auto_role_menu_workflow.detail_modal_description_field"
                        ),
                        default_value=builder.description,
                        min_length=0,
                        max_length=_MAX_MENU_DESCRIPTION_LENGTH
                    ),
                    TextBox(
                        id="tbroles",
                        owner_id=state.owner_id,
                        label=self.__i18n.get(
                            "extensions.admin.auto_role_menu_workflow.detail_modal_roles_field"
                        ),
                        default_value="yes" if builder.show_roles else "no",
                        is_required=True,
                        min_length=1,
                        max_length=3
                    )
                ]
            )
        )

    @modal(
        identifier="armdetailm",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def edit_auto_role_menu_details(
        self,
        context: InteractionContext,
        state: ModalState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (tb_title := state.get_component_state(TextBoxState, "tbtitle"))
            or not (tb_description := state.get_component_state(TextBoxState, "tbdescription"))
            or not (tb_roles := state.get_component_state(TextBoxState, "tbroles"))
            or not tb_title.value
            or not (state_id := tb_title.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        if (
            len(tb_title.value) > _MAX_MENU_TITLE_LENGTH
            or (tb_description.value and len(tb_description.value) > _MAX_MENU_DESCRIPTION_LENGTH)
        ):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.details_too_long_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        builder.title = tb_title.value
        builder.description = tb_description.value
        builder.show_roles = tb_roles.value is not None and tb_roles.value.lower() == "yes"

        embed, components = self.__create_view(builder, False)

        return self._edit_message(
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @staticmethod
    def __get_cache_key(server_id: str, state_id: str) -> str:
        return f"autorole/{server_id}/{state_id}"

    async def __try_remove_role(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (role_id := state.custom_data.get("r"))
            or not (state_id := state.custom_data.get("i"))
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = AutoRoleMenuWorkflow.__get_cache_key(context.server_id, state_id)
        if not (builder := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.builder_expired_error"),
                is_ephemeral=True
            )

        if len(builder.roles) == 1:
            return self._reply(
                content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.cannot_remove_only_role_error"),
                is_ephemeral=True
            )

        for index, options in enumerate(builder.roles):
            if options.role_id == role_id:
                builder.roles.pop(index)
                embed, components = self.__create_view(builder, False)

                return self._edit_message(
                    content=None,
                    embed=embed,
                    components=components,
                    suppress_user_mentions=True
                )

        return self._reply(
            content=self.__i18n.get("extensions.admin.auto_role_menu_workflow.role_not_added_error"),
            is_ephemeral=True
        )

    async def __remove_exclusive_user_roles(
        self,
        context: ServerChatInteractionContext,
    ) -> None:
        if not context.message:
            return

        user_roles = await self.__user_manager.get_role_ids(
            context.server_id,
            context.author_id
        )

        for component in context.message.components:
            if component.identifier != "armgr" or not isinstance(component, ButtonState):
                continue

            role_id = component.custom_data.get("r")
            if not role_id or role_id not in user_roles:
                continue

            await self.__user_manager.remove_role(
                context.server_id,
                context.author_id,
                role_id
            )

    def __create_view(
        self,
        builder: _AutoRoleMenuBuilder,
        is_finalized: bool
    ) -> tuple[Embed, list[LayoutBase]]:
        embed = Embed(
            title=builder.title,
            description=builder.description,
            footer=EmbedFooter(
                text=self.__i18n.get(
                    "extensions.admin.auto_role_menu_workflow.embed_footer"
                )
            )
        )

        if builder.show_roles:
            for role_options in builder.roles:
                embed.fields.append(
                    EmbedField(
                        name=f"{role_options.emoji_mention}",
                        value=f"<@&{role_options.role_id}>"
                    )
                )

        components: list[LayoutBase] = [
            StackLayout(
                id="getrole",
                children=[
                    self.__create_role_button(
                        builder,
                        role,
                        is_finalized
                    ) for role in islice(
                        builder.roles,
                        layout_index * 5,
                        (layout_index + 1) * 5
                    )
                ]
            ) for layout_index in range(ceil(len(builder.roles) / 5.0))
        ]

        if not is_finalized:
            components.append(
                StackLayout(
                    id="getrolectrl",
                    children=[
                        Button(
                            id="armfin",
                            owner_id=builder.owner_id,
                            text="✅",
                            style=ComponentStyle.PRIMARY,
                            custom_data={
                                "i": builder.id
                            }
                        ),
                        Button(
                            id="armeditdetail",
                            owner_id=builder.owner_id,
                            text="📝",
                            style=ComponentStyle.SECONDARY,
                            custom_data={
                                "i": builder.id
                            }
                        ),
                        Button(
                            id="armdel",
                            owner_id=builder.owner_id,
                            text="❌",
                            style=ComponentStyle.SECONDARY,
                            custom_data={
                                "i": builder.id
                            }
                        ),
                        Button(
                            id="armadd",
                            owner_id=builder.owner_id,
                            text="➕",
                            style=ComponentStyle.SECONDARY,
                            custom_data={
                                "i": builder.id
                            }
                        )
                    ]
                )
            )
        else:
            components.append(
                StackLayout(
                    id="getrolectrl",
                    children=[
                        Button(
                            id="armedit",
                            owner_id=builder.owner_id,
                            text="📝",
                            style=ComponentStyle.SECONDARY,
                            custom_data={
                                "e": "1" if builder.is_exclusive else "0",
                                "r": "1" if builder.show_roles else "0"
                            }
                        )
                    ]
                )
            )

        return (embed, components)

    def __create_role_button(
        self,
        builder: _AutoRoleMenuBuilder,
        role_options: _RoleOptions,
        is_finalized: bool
    ) -> Button:
        return Button(
            id="armgr",
            owner_id=builder.owner_id,
            emoji_id=self.__emoji_data_provider.extract_id(role_options.emoji_mention),
            style=ComponentStyle.SECONDARY,
            custom_data={
                "e": "1" if builder.is_exclusive else "0",
                "r": role_options.role_id,
                "f": "1" if is_finalized else "0",
                "i": builder.id
            }
        )
