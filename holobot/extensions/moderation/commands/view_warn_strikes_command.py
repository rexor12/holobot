from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.components import Paginator
from holobot.discord.sdk.components.models import (
    ComponentInteractionResponse, ComponentRegistration, PagerState
)
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, Union

DEFAULT_PAGE_SIZE = 5

@injectable(CommandInterface)
class ViewWarnStrikesCommand(ModerationCommandBase):
    def __init__(
        self,
        log: LogInterface,
        member_data_provider: IMemberDataProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__("view")
        self.group_name = "moderation"
        self.subgroup_name = "warns"
        self.description = "Displays a user's warn strikes"
        self.options = [
            Option("user", "The mention of the user to inspect.")
        ]
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.components = [
            ComponentRegistration("warn_paginator", Paginator, self.__on_page_changed, DeferType.DEFER_MESSAGE_UPDATE)
        ]
        self.__log: LogInterface = log.with_name("Moderation", "ViewWarnStrikesCommand")
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: ServerChatInteractionContext, user: str) -> CommandResponse:
        user = user.strip()
        if (user_id := get_user_id(user)) is None:
            return CommandResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        if not self.__member_data_provider.is_member(context.server_id, user_id):
            return CommandResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )

        return CommandResponse(ReplyAction(
            await self.__create_page_content(context.server_id, user_id, 0, DEFAULT_PAGE_SIZE),
            Paginator("warn_paginator", current_page=0)
        ))

    async def __on_page_changed(
        self,
        _registration: ComponentRegistration,
        context: InteractionContext,
        state: Any
    ) -> ComponentInteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return ComponentInteractionResponse(EditMessageAction("An internal error occurred while processing the interaction."))

        return ComponentInteractionResponse(
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
