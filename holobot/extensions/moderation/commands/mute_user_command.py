from .moderation_command_base import ModerationCommandBase
from .responses import UserMutedResponse
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.chrono import parse_interval
from typing import Optional

@injectable(CommandInterface)
class MuteUserCommand(ModerationCommandBase):
    def __init__(self, messaging: IMessaging, mute_manager: IMuteManager) -> None:
        super().__init__("mute")
        self.group_name = "moderation"
        self.description = "Mutes a user."
        self.options = [
            create_option("user", "The mention of the user to mute.", SlashCommandOptionType.STRING, True),
            create_option("reason", "The reason of the punishment.", SlashCommandOptionType.STRING, True),
            create_option("duration", "The duration after which to lift the mute. Eg. 1h or 30m.", SlashCommandOptionType.STRING, False)
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
        self.__messaging: IMessaging = messaging
        self.__mute_manager: IMuteManager = mute_manager
    
    async def execute(self, context: SlashContext, user: str, reason: str, duration: Optional[str] = None) -> CommandResponse:
        user = user.strip()
        reason = reason.strip()
        mute_duration = parse_interval(duration.strip()) if duration is not None else None
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return CommandResponse()
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return CommandResponse()

        try:
            await self.__mute_manager.mute_user(str(context.guild_id), user_id, reason, mute_duration)
        except ArgumentOutOfRangeError as error:
            if error.argument_name == "reason":
                await reply(context, f"The reason parameter's length must be between {error.lower_bound} and {error.upper_bound}.")
            elif error.argument_name == "duration":
                await reply(context, f"The duration parameter's value must be between {error.lower_bound} and {error.upper_bound}.")
            return CommandResponse()
        except UserNotFoundError:
            await reply(context, "The user you mentioned cannot be found.")
            return CommandResponse()
        except ForbiddenError:
            await reply(context, (
                "I cannot assign/create a 'Muted' role.\n"
                "Have you given me role management permissions?\n"
                "Do they have a role ranking higher than mine?"
            ))
            return CommandResponse()

        try:
            await self.__messaging.send_dm(user_id, f"You have been muted in {context.guild.name} by {context.author.name} with the reason '{reason}'. I'm sorry this happened to you.")
        except ForbiddenError:
            pass

        await reply(context, f"<@{user_id}> has been muted. Reason: {reason}")
        return UserMutedResponse(
            author_id=str(context.author_id),
            user_id=user_id,
            reason=reason,
            duration=mute_duration
        )
