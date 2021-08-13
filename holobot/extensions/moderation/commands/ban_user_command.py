from .moderation_command_base import ModerationCommandBase
from .. import IConfigProvider
from ..enums import ModeratorPermission
from discord.errors import Forbidden
from discord.member import Member
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class BanUserCommand(ModerationCommandBase):
    def __init__(self, config_provider: IConfigProvider, messaging: MessagingInterface) -> None:
        super().__init__("ban")
        self.group_name = "moderation"
        self.description = "Bans a user from the server. The user cannot rejoin until the ban is lifted."
        self.options = [
            create_option("user", "The mention of the user to ban.", SlashCommandOptionType.STRING, True),
            create_option("reason", "The reason of the punishment.", SlashCommandOptionType.STRING, True),
            create_option("days", "If specified, the previous N days' messages are also removed.", SlashCommandOptionType.INTEGER, False)
        ]
        self.required_moderator_permissions = ModeratorPermission.BAN_USERS
        self.__config_provider: IConfigProvider = config_provider
        self.__messaging: MessagingInterface = messaging
    
    async def execute(self, context: SlashContext, user: str, reason: str, days: Optional[int] = None) -> None:
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return
        days = days if days is not None else 0
        if days < 0 or days > 7:
            await reply(context, "The days parameter's value must be between 0 and 7. If omitted, no messages are deleted.")
            return
        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            await reply(context, f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}.")
            return

        member = context.guild.get_member(int(user_id))
        if member is None:
            await reply(context, "The user you mentioned cannot be found.")
            return
        if not isinstance(member, Member):
            await reply(context, "I'm sorry, but something went wrong internally. Please, try again later or contact your server administrator.")
            return
        
        try:
            await member.ban(reason=reason, delete_message_days=days)
        except Forbidden:
            await reply(context, (
                "I cannot ban the user.\n"
                "Have you given me user management permissions?\n"
                "Do they have a higher ranking role?"
            ))
            return

        await self.__messaging.send_dm(user_id, f"You have been banned from {context.guild.name} by {context.author.name} with the reason '{reason}'. I'm sorry this happened to you.")
        await reply(context, f"{member.mention} has been banned. Reason: {reason}")
