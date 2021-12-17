from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import textify_timedelta

@injectable(CommandInterface)
class ViewWarnDecayCommand(CommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("viewdecay")
        self.group_name = "moderation"
        self.subgroup_name = "warns"
        self.description = "Displays the currently set warn decay."
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        decay_threshold = await self.__warn_manager.get_warn_decay(context.server_id)
        return CommandResponse(action=ReplyAction(
            content=f"The warn decay is set to {textify_timedelta(decay_threshold)}."
                    if decay_threshold else "There is no warn decay set for the server."
        ))
