from .. import AlertManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAllAlarmsCommand(CommandBase):
    def __init__(self, alert_manager: AlertManagerInterface) -> None:
        super().__init__("removeall")
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.group_name = "crypto"
        self.subgroup_name = "alarm"
        self.description = "Removes ALL of your alarms."

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        await self.__alert_manager.remove_all(context.author_id)
        return CommandResponse(
            action=ReplyAction(content="All of your alarms have been removed.")
        )
