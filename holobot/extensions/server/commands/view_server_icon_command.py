from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ServerNotFoundError
from holobot.discord.sdk.models import Embed
from holobot.discord.sdk.servers import IServerDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ViewServerIconCommand(CommandBase):
    def __init__(self, server_data_provider: IServerDataProvider) -> None:
        super().__init__("icon")
        self.group_name = "server"
        self.description = "Displays the server's icon."
        self.__server_data_provider: IServerDataProvider = server_data_provider

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        try:
            server = self.__server_data_provider.get_basic_data_by_id(context.server_id)
        except ServerNotFoundError:
            return CommandResponse(
                action=ReplyAction(content="The server cannot be found.")
            )
        
        if not server.icon_url:
            return CommandResponse(action=ReplyAction(content="The server doesn't have an icon."))
        
        return CommandResponse(
            action=ReplyAction(content=Embed(
                title=f"{server.name}'s icon",
                image_url=server.icon_url
            ))
        )
