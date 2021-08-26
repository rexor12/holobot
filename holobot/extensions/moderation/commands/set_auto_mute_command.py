from typing import Optional
from .moderation_command_base import ModerationCommandBase
from .responses import AutoMuteToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class SetAutoMuteCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("setmute")
        self.group_name = "moderation"
        self.subgroup_name = "auto"
        self.description = "Enables automatic muting of people with warn strikes."
        self.options = [
            Option("warn_count", "The number of warns after which a user is automatically muted.", OptionType.INTEGER,),
            Option("duration", "The duration after which the user is automatically unmuted. Eg. 1d, 1h or 30m.", is_mandatory=False)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: ServerChatInteractionContext, warn_count: int, duration: Optional[str] = None) -> CommandResponse:
        mute_duration = parse_interval(duration.strip()) if duration is not None else None
        try:
            await self.__warn_manager.enable_auto_mute(context.server_id, warn_count, mute_duration)
        except ArgumentOutOfRangeError as error:
            if error.argument_name == "duration":
                return CommandResponse(
                    action=ReplyAction(content=f"The duration must be between {error.lower_bound} and {error.upper_bound}.")
                )
            return CommandResponse(
                action=ReplyAction(content=f"The warn count must be between {error.lower_bound} and {error.upper_bound}.")
            )

        return AutoMuteToggledResponse(
            author_id=str(context.author_id),
            is_enabled=True,
            warn_count=warn_count,
            duration=mute_duration,
            action=ReplyAction(content="Auto mute has been configured.")
        )
