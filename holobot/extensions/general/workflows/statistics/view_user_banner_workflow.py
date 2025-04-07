from dataclasses import dataclass

from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentStyle, LayoutBase, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext, View
from holobot.sdk.i18n import localize
from holobot.sdk.ioc.decorators import injectable

@dataclass
class _BannerDescriptor:
    user_name: str
    has_server_banner: bool
    has_global_banner: bool
    is_server_banner: bool
    banner_url: str | None
    role_color: int | None

@injectable(IWorkflow)
class ViewUserBannerWorkflow(WorkflowBase):
    def __init__(
        self,
        member_data_provider: IMemberDataProvider,
        user_data_provider: IUserDataProvider
    ) -> None:
        super().__init__()
        self.__member_data_provider = member_data_provider
        self.__user_data_provider = user_data_provider

    @command(
        description="Displays a user's banner.",
        name="banner",
        options=(
            Option(
                "user",
                "The user to view. By default, it's yourself.",
                type=OptionType.USER,
                is_mandatory=False,
                argument_name="user_id"
            ),
            Option(
                "type",
                "The type of banner you want to see.",
                type=OptionType.INTEGER,
                is_mandatory=False,
                choices=(
                    Choice("Global", 0),
                    Choice("Server", 1)
                ),
                argument_name="is_server_banner",
            )
        )
    )
    async def view_user_banner(
        self,
        context: InteractionContext,
        user_id: int | None = None,
        is_server_banner: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=localize("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__get_banner_response(
            context.server_id,
            user_id or context.author_id,
            True if is_server_banner != False else False,
            context.author_id
        )

        return self._reply(
            content=content,
            embed=embed,
            components=components,
            suppress_user_mentions=True
        )

    @component(identifier="ubannerg", is_bound=True)
    async def view_user_global_banner(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (user_id := get_custom_int(state.custom_data, "u"))
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__get_banner_response(
            context.server_id,
            user_id,
            False,
            context.author_id
        )

        return self._clear_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(identifier="ubanners", is_bound=True)
    async def view_user_server_banner(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (user_id := get_custom_int(state.custom_data, "u"))
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__get_banner_response(
            context.server_id,
            user_id,
            True,
            context.author_id
        )

        return self._clear_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __get_banner_response(
        self,
        server_id: int | None,
        user_id: int,
        request_server_banner: bool,
        owner_id: int
    ) -> View:
        try:
            descriptor = await self.__get_banner(
                server_id,
                user_id,
                request_server_banner
            )

            if not descriptor.banner_url:
                return View(
                    content=localize(
                        "extensions.general.view_user_banner_workflow.no_banner_error",
                        { "user_id": user_id }
                    )
                )

            return View(
                embed=Embed(
                    title=localize(
                        "extensions.general.view_user_banner_workflow.embed_title_server"
                        if descriptor.is_server_banner
                        else "extensions.general.view_user_banner_workflow.embed_title_global",
                        { "user": descriptor.user_name }
                    ),
                    color=descriptor.role_color,
                    image_url=descriptor.banner_url
                ),
                components=self.__get_banner_buttons(user_id, descriptor, owner_id)
            )
        except UserNotFoundError:
            return View(
                content=localize("user_not_found_error")
            )
        except ServerNotFoundError:
            return View(
                content=localize("server_not_found_error")
            )
        except ChannelNotFoundError:
            return View(
                content=localize("channel_not_found_error")
            )

    def __get_banner_buttons(
        self,
        user_id: int,
        descriptor: _BannerDescriptor,
        owner_id: int
    ) -> list[LayoutBase] | None:
        if not descriptor.has_global_banner or not descriptor.has_server_banner:
            return None

        layout = StackLayout(id="dummy", children=[])
        if descriptor.has_global_banner:
            layout.children.append(
                Button(
                    id="ubannerg",
                    owner_id=owner_id,
                    text=localize("extensions.general.view_user_banner_workflow.global_button"),
                    style=(
                        ComponentStyle.PRIMARY
                        if not descriptor.is_server_banner
                        else ComponentStyle.SECONDARY
                    ),
                    is_enabled=descriptor.is_server_banner,
                    custom_data={ "u": str(user_id) }
                )
            )
        if descriptor.has_server_banner:
            layout.children.append(
                Button(
                    id="ubanners",
                    owner_id=owner_id,
                    text=localize("extensions.general.view_user_banner_workflow.server_button"),
                    style=(
                        ComponentStyle.PRIMARY
                        if descriptor.is_server_banner
                        else ComponentStyle.SECONDARY
                    ),
                    is_enabled=not descriptor.is_server_banner,
                    custom_data={ "u": str(user_id) }
                )
            )

        return [layout]

    async def __get_banner(
        self,
        server_id: int | None,
        user_id: int,
        request_server_banner: bool
    ) -> _BannerDescriptor:
        if server_id:
            descriptor = await self.__get_banner_by_server(
                server_id,
                user_id,
                request_server_banner
            )
            if descriptor.banner_url:
                return descriptor

        # NOTE: Avoid using the cache because this great platform is inconsistent
        # about sending banner URLs. A direct REST API call will return them.
        user = await self.__user_data_provider.get_user_data_by_id(user_id, False)

        return _BannerDescriptor(
            user.name,
            False,
            bool(user.banner_url),
            False,
            user.banner_url,
            None
        )

    async def __get_banner_by_server(
        self,
        server_id: int,
        user_id: int,
        request_server_banner: bool
    ) -> _BannerDescriptor:
        # NOTE: Avoid using the cache because this great platform is inconsistent
        # about sending banner URLs. A direct REST API call will return them.
        member = await self.__member_data_provider.get_basic_data_by_id(
            server_id,
            user_id,
            False
        )

        if request_server_banner and member.server_specific_banner_url:
            return _BannerDescriptor(
                member.name,
                True,
                bool(member.banner_url),
                True,
                member.server_specific_banner_url,
                member.color
            )

        return _BannerDescriptor(
            member.name,
            bool(member.server_specific_banner_url),
            bool(member.banner_url),
            False,
            member.banner_url,
            member.color
        )
