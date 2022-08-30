from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ServerNotFoundError
from holobot.discord.sdk.models import Embed
from holobot.discord.sdk.servers import IServerDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import EntityType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ViewServerIconWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        server_data_provider: IServerDataProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__server_data_provider = server_data_provider

    @command(
        description="Displays the server's icon.",
        name="icon",
        group_name="server",
        cooldown=Cooldown(duration=10, entity_type=EntityType.SERVER)
    )
    async def display_server_icon(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        try:
            server = self.__server_data_provider.get_basic_data_by_id(context.server_id)
        except ServerNotFoundError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("server_not_found_error"))
            )

        if not server.icon_url:
            return InteractionResponse(ReplyAction(content=self.__i18n_provider.get(
                    "extensions.server.view_server_icon_workflow.no_server_icon"
                )))

        return InteractionResponse(
            action=ReplyAction(content=Embed(
                title=self.__i18n_provider.get(
                    "extensions.server.view_server_icon_workflow.embed_title",
                    { "name": server.name }
                ),
                image_url=server.icon_url
            ))
        )
