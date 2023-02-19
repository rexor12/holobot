from holobot.discord.sdk.exceptions import ServerNotFoundError
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.servers import IServerDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import EntityType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ViewServerBannerWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        server_data_provider: IServerDataProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__server_data_provider = server_data_provider

    @command(
        description="Displays the server's banner.",
        name="banner",
        group_name="server",
        cooldown=Cooldown(duration=10, entity_type=EntityType.SERVER)
    )
    async def display_server_banner(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        try:
            server = await self.__server_data_provider.get_basic_data_by_id(context.server_id)
        except ServerNotFoundError:
            return self._reply(content=self.__i18n_provider.get("server_not_found_error"))

        if not server.banner_url:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.server.view_server_banner_workflow.no_server_banner"
                )
            )

        return self._reply(
            embed=Embed(
                title=self.__i18n_provider.get(
                    "extensions.server.view_server_banner_workflow.embed_title",
                    { "name": server.name }
                ),
                image_url=server.banner_url
            )
        )
