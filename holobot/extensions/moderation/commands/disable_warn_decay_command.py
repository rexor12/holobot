from .moderation_command_base import ModerationCommandBase
from .responses import WarnDecayToggledResponse
from ..managers import IWarnManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class DisableWarnDecayCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("disabledecay")
        self.group_name = "moderation"
        self.subgroup_name = "warns"
        self.description = "Disables automatic warn strike removal."
        self.required_permissions = Permission.ADMINISTRATOR
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        await self.__warn_manager.set_warn_decay(context.server_id, None)
        return WarnDecayToggledResponse(
            author_id=context.author_id,
            action=ReplyAction(content="Warn strikes won't be removed automatically anymore.")
        )
