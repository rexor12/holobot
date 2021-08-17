from .moderation_command_base import ModerationCommandBase
from .responses import UserUnmutedResponse
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class UnmuteUserCommand(ModerationCommandBase):
    def __init__(self, mute_manager: IMuteManager) -> None:
        super().__init__("unmute")
        self.group_name = "moderation"
        self.description = "Removes the muting from a user."
        self.options = [
            create_option("user", "The mention of the user to mute.", SlashCommandOptionType.STRING, True)
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
        self.__mute_manager: IMuteManager = mute_manager
    
    async def execute(self, context: SlashContext, user: str) -> CommandResponse:
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return CommandResponse()
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return CommandResponse()

        try:
            await self.__mute_manager.unmute_user(str(context.guild_id), user_id)
        except UserNotFoundError:
            await reply(context, "The user you mentioned cannot be found.")
            return CommandResponse()
        except ForbiddenError:
            await reply(context, (
                "I cannot remove the 'Muted' role.\n"
                "Have you given me role management permissions?\n"
                "Do they have a role ranking higher than mine?"
            ))
            return CommandResponse()

        await reply(context, f"<@{user_id}> has been unmuted.")
        return UserUnmutedResponse(
            author_id=str(context.author_id),
            user_id=user_id
        )
