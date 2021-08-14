from .. import AlertManagerInterface
from discord_slash import SlashContext
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAllAlarmsCommand(CommandBase):
    def __init__(self, alert_manager: AlertManagerInterface) -> None:
        super().__init__("removeall")
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.group_name = "crypto"
        self.subgroup_name = "alarm"
        self.description = "Removes ALL of your alarms."

    async def execute(self, context: SlashContext) -> CommandResponse:
        await self.__alert_manager.remove_all(get_author_id(context))
        await reply(context, "All of your alarms have been removed.")
        return CommandResponse()
