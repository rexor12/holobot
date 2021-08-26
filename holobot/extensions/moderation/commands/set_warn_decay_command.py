from .moderation_command_base import ModerationCommandBase
from .responses import WarnDecayToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class SetWarnDecayCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("setdecay")
        self.group_name = "moderation"
        self.subgroup_name = "warns"
        self.description = "Enables automatic warn strike removal."
        self.options = [
            Option("duration", "The duration after which a warn strike is removed from a user. Eg. 1d, 1h or 30m.")
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: ServerChatInteractionContext, duration: str) -> CommandResponse:
        decay_threshold = parse_interval(duration.strip())
        try:
            await self.__warn_manager.set_warn_decay(context.server_id, decay_threshold)
        except ArgumentOutOfRangeError as error:
            return CommandResponse(
                action=ReplyAction(content=f"The duration must be between {error.lower_bound} and {error.upper_bound}.")
            )

        return WarnDecayToggledResponse(
            author_id=str(context.author_id),
            is_enabled=True,
            duration=decay_threshold,
            action=ReplyAction(content="The warn decay time has been set.")
        )
