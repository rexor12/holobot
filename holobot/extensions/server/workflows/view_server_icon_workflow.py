from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ServerNotFoundError
from holobot.discord.sdk.models import Embed
from holobot.discord.sdk.servers import IServerDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ViewServerIconWorkflow(WorkflowBase):
    def __init__(self, server_data_provider: IServerDataProvider) -> None:
        super().__init__()
        self.__server_data_provider: IServerDataProvider = server_data_provider

    @command(
        description="Displays the server's icon.",
        name="icon",
        group_name="server"
    )
    async def display_server_icon(self, context: ServerChatInteractionContext) -> InteractionResponse:
        try:
            server = self.__server_data_provider.get_basic_data_by_id(context.server_id)
        except ServerNotFoundError:
            return InteractionResponse(
                action=ReplyAction(content="The server cannot be found.")
            )
        
        if not server.icon_url:
            return InteractionResponse(action=ReplyAction(content="The server doesn't have an icon."))
        
        return InteractionResponse(
            action=ReplyAction(content=Embed(
                title=f"{server.name}'s icon",
                image_url=server.icon_url
            ))
        )
