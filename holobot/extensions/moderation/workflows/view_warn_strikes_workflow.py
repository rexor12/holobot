from typing import Any

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from .interactables.decorators import moderation_command, moderation_component

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewWarnStrikesWorkflow(WorkflowBase):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        member_data_provider: IMemberDataProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(ViewWarnStrikesWorkflow)
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__warn_manager: IWarnManager = warn_manager

    @moderation_command(
        description="Displays a user's warn strikes",
        name="view",
        group_name="moderation",
        subgroup_name="warns",
        options=(
            Option("user", "The mention of the user to inspect."),
        ),
        required_moderator_permissions=ModeratorPermission.WARN_USERS
    )
    async def view_warn_strikes(
        self,
        context: ServerChatInteractionContext,
        user: str
    ) -> InteractionResponse:
        user = user.strip()
        if (user_id := get_user_id(user)) is None:
            return self._reply(content="You must mention a user correctly.")

        if not await self.__member_data_provider.is_member(context.server_id, user_id):
            return self._reply(content="The user you mentioned cannot be found.")

        content, embed, components = await self.__create_page_content(
            context.server_id,
            user_id,
            0,
            DEFAULT_PAGE_SIZE
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @moderation_component(
        identifier="warn_paginator",
        component_type=Paginator,
        is_bound=True,
        required_moderator_permissions=ModeratorPermission.WARN_USERS,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(content="An internal error occurred while processing the interaction.")

        content, embed, components = await self.__create_page_content(
            context.server_id,
            state.owner_id,
            max(state.current_page, 0),
            DEFAULT_PAGE_SIZE
        )

        return (
            self._edit_message(
                content=content,
                embed=embed,
                components=components
            )
            if isinstance(state, PagerState)
            else self._edit_message(content="An internal error occurred while processing the interaction.")
        )

    async def __create_page_content(
        self,
        server_id: str,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        self.__logger.trace(
            "User requested warn strike page",
            server_id=server_id,
            user_id=user_id,
            page_index=page_index
        )
        result = await self.__warn_manager.get_warns(server_id, user_id, page_index, page_size)
        if not result.items:
            return ("The user has no warn strikes.", None, None)

        embed = Embed(
            title="Warn strikes",
            description=f"The list of warn strikes of <@{user_id}>."
        )

        for warn_strike in result.items:
            embed.fields.append(EmbedField(
                name=f"Strike #{warn_strike.identifier}",
                value=(
                    f"> Reason: {warn_strike.reason}\n"
                    f"> Warned by <@{warn_strike.warner_id}> at {warn_strike.created_at:%I:%M:%S %p, %m/%d/%Y %Z}"
                ),
                is_inline=False
            ))

        component = Paginator(
            id="warn_paginator",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count
        )

        return (None, embed, component)
