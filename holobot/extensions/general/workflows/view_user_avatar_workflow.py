from dataclasses import dataclass
from enum import IntEnum, unique
from typing import Any

from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.models import Embed, EmbedFooter, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.servers.models import MemberData
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComponentBase, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import ButtonState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models import AvatarOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@unique
class _AvatarKind(IntEnum):
    GLOBAL = 0
    SERVER_SPECIFIC = 1

_AVATAR_KIND_PRIORITY = [_AvatarKind.SERVER_SPECIFIC, _AvatarKind.GLOBAL]

@dataclass
class _AvatarInfo:
    avatar_urls: dict[_AvatarKind, str | None]
    effective_avatar_kind: _AvatarKind | None
    effective_avatar_url: str | None

@injectable(IWorkflow)
class ViewUserAvatarWorkflow(WorkflowBase):
    def __init__(
        self,
        bot_data_provider: IBotDataProvider,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        options: IOptions[AvatarOptions]
    ) -> None:
        super().__init__()
        self.__bot_data_provider = bot_data_provider
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__options = options

    @command(
        description="Displays a user's avatar.",
        name="avatar",
        options=(
            Option(
                "user",
                "The name or mention of the user. By default, it's yourself.",
                is_mandatory=False
            ),
        )
    )
    async def view_user_avatar(
        self,
        context: InteractionContext,
        user: str | None = None,
        kind: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        if kind is None:
            avatar_kind = _AvatarKind.SERVER_SPECIFIC
        else:
            try:
                avatar_kind = _AvatarKind(kind)
            except ValueError:
                return self._reply(content=self.__i18n_provider.get("invalid_argument_error"))
            else:
                avatar_kind = _AvatarKind.SERVER_SPECIFIC

        content, components = await self.__get_response_view(context, user, False, avatar_kind)

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=content if isinstance(content, Embed) else None,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="avatar_global",
        component_type=Button
    )
    async def view_global_user_avatar(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, ButtonState) or not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        content, components = await self.__get_response_view(
            context,
            state.custom_data.get("uid", context.author_id),
            True,
            _AvatarKind.GLOBAL
        )

        return self._edit_message(
            content=content if isinstance(content, str) else None,
            embed=content if isinstance(content, Embed) else None,
            components=components,
            suppress_user_mentions=True
        )

    @component(
        identifier="avatar_server",
        component_type=Button
    )
    async def view_server_user_avatar(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, ButtonState) or not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        content, components = await self.__get_response_view(
            context,
            state.custom_data.get("uid", context.author_id),
            True,
            _AvatarKind.SERVER_SPECIFIC
        )

        return self._edit_message(
            content=content if isinstance(content, str) else None,
            embed=content if isinstance(content, Embed) else None,
            components=components,
            suppress_user_mentions=True
        )

    @staticmethod
    def __get_avatar_info(
        member_data: MemberData,
        avatar_kind: _AvatarKind
    ) -> _AvatarInfo:
        avatar_urls = {
            _AvatarKind.GLOBAL: member_data.avatar_url,
            _AvatarKind.SERVER_SPECIFIC: member_data.server_specific_avatar_url
        }

        def get_effective_avatar(
            urls: dict[_AvatarKind, str | None],
            kind: _AvatarKind
        ) -> tuple[_AvatarKind, str] | None:
            if url := urls.get(kind, None):
                return (kind, url)

            for kind in _AVATAR_KIND_PRIORITY:
                if url := urls.get(kind, None):
                    return (kind, url)

            return None

        effective_value = get_effective_avatar(avatar_urls, avatar_kind)

        return _AvatarInfo(
            avatar_urls=avatar_urls,
            effective_avatar_kind=effective_value[0] if effective_value else None,
            effective_avatar_url=effective_value[1] if effective_value else None
        )

    async def __get_member(
        self,
        context: ServerChatInteractionContext,
        user_name_or_mention_or_id: str | None,
        is_user_id: bool
    ) -> MemberData:
        if not user_name_or_mention_or_id:
            return await self.__member_data_provider.get_basic_data_by_id(
                context.server_id,
                context.author_id
            )

        if is_user_id:
            return await self.__member_data_provider.get_basic_data_by_id(
                context.server_id,
                user_name_or_mention_or_id
            )

        if (user_id := get_user_id(user_name_or_mention_or_id)) is not None:
            return await self.__member_data_provider.get_basic_data_by_id(
                context.server_id,
                user_id
            )

        return await self.__member_data_provider.get_basic_data_by_name(
            context.server_id,
            user_name_or_mention_or_id.strip()
        )

    async def __get_response_view(
        self,
        context: ServerChatInteractionContext,
        user_name_or_mention: str | None,
        is_user_id: bool,
        avatar_kind: _AvatarKind
    ) -> tuple[Embed | str, ComponentBase | None]:

        try:
            member_data = await self.__get_member(context, user_name_or_mention, is_user_id)
        except UserNotFoundError:
            return (self.__i18n_provider.get("user_not_found_error"), None)
        except ServerNotFoundError:
            return (self.__i18n_provider.get("server_not_found_error"), None)
        except ChannelNotFoundError:
            return (self.__i18n_provider.get("channel_not_found_error"), None)

        avatar_info = ViewUserAvatarWorkflow.__get_avatar_info(member_data, avatar_kind)
        if not (avatar_url := avatar_info.effective_avatar_url):
            return (
                self.__i18n_provider.get(
                    "extensions.general.view_user_avatar_workflow.no_avatar_error",
                    { "user_id": member_data.user_id }
                ),
                None
            )

        if member_data.user_id == self.__bot_data_provider.get_user_id():
            footer = EmbedFooter(
                text=self.__i18n_provider.get(
                    "extensions.general.view_user_avatar_workflow.embed_footer",
                    { "artist": self.__options.value.ArtworkArtistName }
                )
            )
        else:
            footer = None

        global_button_enabled = (
            avatar_info.effective_avatar_kind is not None
            and avatar_info.effective_avatar_kind is not _AvatarKind.GLOBAL
            and bool(avatar_info.avatar_urls.get(_AvatarKind.GLOBAL, None))
        )
        server_button_enabled = (
            avatar_info.effective_avatar_kind is not None
            and avatar_info.effective_avatar_kind is not _AvatarKind.SERVER_SPECIFIC
            and bool(avatar_info.avatar_urls.get(_AvatarKind.SERVER_SPECIFIC, None))
        )

        layout = None
        if global_button_enabled or server_button_enabled:
            custom_data: dict[str, str] = {
                "uid": member_data.user_id
            }
            buttons: list[ComponentBase] = [
                Button(
                    id="avatar_global",
                    owner_id=context.author_id,
                    text=self.__i18n_provider.get(
                        "extensions.general.view_user_avatar_workflow.global_button"
                    ),
                    style=ComponentStyle.SECONDARY,
                    is_enabled=global_button_enabled,
                    custom_data=custom_data
                ),
                Button(
                    id="avatar_server",
                    owner_id=context.author_id,
                    text=self.__i18n_provider.get(
                        "extensions.general.view_user_avatar_workflow.server_button"
                    ),
                    style=ComponentStyle.SECONDARY,
                    is_enabled=server_button_enabled,
                    custom_data=custom_data
                )
            ]
            layout = StackLayout(
                id="avatar_buttons",
                children=buttons
            )

        embed_title_i18n_key = (
            "extensions.general.view_user_avatar_workflow.embed_title_server"
            if avatar_info.effective_avatar_kind is _AvatarKind.SERVER_SPECIFIC
            else "extensions.general.view_user_avatar_workflow.embed_title_global"
        )

        return (
            Embed(
                title=self.__i18n_provider.get(
                    embed_title_i18n_key,
                    { "user": member_data.display_name }
                ),
                image_url=avatar_url,
                footer=footer
            ),
            layout
        )
