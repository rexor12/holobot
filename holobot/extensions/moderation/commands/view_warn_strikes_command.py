from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from discord.embeds import Embed
from discord.member import Member
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.components import DynamicPager
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(CommandInterface)
class ViewWarnStrikesCommand(ModerationCommandBase):
    def __init__(self, log: LogInterface, messaging: MessagingInterface, warn_manager: IWarnManager) -> None:
        super().__init__("view")
        self.group_name = "moderation"
        self.subgroup_name = "warns"
        self.description = "Displays a user's warn strikes"
        self.options = [
            create_option("user", "The mention of the user to inspect.", SlashCommandOptionType.STRING, True)
        ]
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.__log: LogInterface = log.with_name("Moderation", "ViewWarnStrikesCommand")
        self.__messaging: MessagingInterface = messaging
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: SlashContext, user: str) -> None:
        # TODO Reason length validation + trim.
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return

        member = context.guild.get_member(int(user_id))
        if member is None:
            await reply(context, "The user you mentioned cannot be found.")
            return
        if not isinstance(member, Member):
            await reply(context, "I'm sorry, but something went wrong internally. Please, try again later or contact your server administrator.")
            return
        
        await DynamicPager(self.__messaging, self.__log, context,
            lambda _, page_index, page_size: self.__create_embed(str(context.guild_id), user_id, page_index, page_size))

    async def __create_embed(self, server_id: str, user_id: Optional[str], page_index: int, page_size: int) -> Optional[Embed]:
        if user_id is None:
            return None

        warn_strikes = await self.__warn_manager.get_warns(server_id, user_id, page_index, page_size)
        if len(warn_strikes) == 0:
            return None

        embed = Embed(
            title="Warn strikes",
            description=f"The list of warn strikes of <@{user_id}>.",
            color=0xeb7d00
        )

        for warn_strike in warn_strikes:
            embed.add_field(
                name=f"Strike #{warn_strike.id}",
                value=(
                    f"> Reason: {warn_strike.reason}\n"
                    f"> Warned by <@{warn_strike.warner_id}> at {warn_strike.created_at:%I:%M:%S %p, %m/%d/%Y %Z}"
                ),
                inline=False
            )
        return embed
