from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.components import Pager
from holobot.discord.sdk.exceptions import UserNotFoundError
from holobot.discord.sdk.models import Embed, EmbedField
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(CommandInterface)
class ViewWarnStrikesCommand(ModerationCommandBase):
    def __init__(self, log: LogInterface, member_data_provider: IMemberDataProvider, messaging: IMessaging, warn_manager: IWarnManager) -> None:
        super().__init__("view")
        self.group_name = "moderation"
        self.subgroup_name = "warns"
        self.description = "Displays a user's warn strikes"
        self.options = [
            Option("user", "The mention of the user to inspect.")
        ]
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.__log: LogInterface = log.with_name("Moderation", "ViewWarnStrikesCommand")
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__messaging: IMessaging = messaging
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

        await Pager(self.__messaging, self.__log, context,
            lambda _, page_index, page_size: self.__create_embed(context.server_id, user_id, page_index, page_size))
        return CommandResponse()

    async def __create_embed(self, server_id: str, user_id: Optional[str], page_index: int, page_size: int) -> Optional[Embed]:
        if user_id is None:
            return None

        warn_strikes = await self.__warn_manager.get_warns(server_id, user_id, page_index, page_size)
        if len(warn_strikes) == 0:
            return None

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
