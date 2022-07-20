from typing import Any, Union

from .interactables.decorators import moderation_command, moderation_component
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Paginator
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewWarnStrikesWorkflow(WorkflowBase):
    def __init__(
        self,
        log: LogInterface,
        member_data_provider: IMemberDataProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "ViewWarnStrikesWorkflow")
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
            return InteractionResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        if not self.__member_data_provider.is_member(context.server_id, user_id):
            return InteractionResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )

        return InteractionResponse(ReplyAction(
            await self.__create_page_content(context.server_id, user_id, 0, DEFAULT_PAGE_SIZE),
            Paginator("warn_paginator", current_page=0)
        ))

    @moderation_component(
        identifier="warn_paginator",
        component_type=Paginator,
        required_moderator_permissions=ModeratorPermission.WARN_USERS,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return InteractionResponse(EditMessageAction("An internal error occurred while processing the interaction."))

        return InteractionResponse(
            EditMessageAction(
                await self.__create_page_content(
                    context.server_id,
                    context.author_id,
                    max(state.current_page, 0),
                    DEFAULT_PAGE_SIZE
                ),
                Paginator("warn_paginator", current_page=max(state.current_page, 0))
            )
            if isinstance(state, PagerState)
            else EditMessageAction("An internal error occurred while processing the interaction.")
        )

    async def __create_page_content(
        self,
        server_id: str,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> Union[str, Embed]:
        self.__log.trace(f"User requested warn strike page. {{ ServerId = {server_id}, UserId = {user_id}, Page = {page_index} }}")
        warn_strikes = await self.__warn_manager.get_warns(server_id, user_id, page_index, page_size)
        if len(warn_strikes) == 0:
            return "The user has no warn strikes."

        embed = Embed(
            title="Warn strikes",
            description=f"The list of warn strikes of <@{user_id}>."
        )

        for warn_strike in warn_strikes:
            embed.fields.append(EmbedField(
                name=f"Strike #{warn_strike.id}",
                value=(
                    f"> Reason: {warn_strike.reason}\n"
                    f"> Warned by <@{warn_strike.warner_id}> at {warn_strike.created_at:%I:%M:%S %p, %m/%d/%Y %Z}"
                ),
                is_inline=False
            ))

        return embed