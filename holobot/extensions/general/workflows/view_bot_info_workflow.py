from datetime import datetime

import tzlocal

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import EnvironmentInterface

@injectable(IWorkflow)
class ViewBotInfoWorkflow(WorkflowBase):
    def __init__(
        self,
        bot_data_provider: IBotDataProvider,
        environment: EnvironmentInterface
    ) -> None:
        super().__init__()
        self.__bot_data_provider: IBotDataProvider = bot_data_provider
        self.__environment = environment

    @command(description="Displays some information about the bot.", name="info")
    async def view_bot_info(self, context: ServerChatInteractionContext) -> InteractionResponse:
        current_time = datetime.now(tzlocal.get_localzone())
        return InteractionResponse(
            action=ReplyAction(Embed(
                title="Bot information",
                description="Basic information about the bot.",
                thumbnail_url=self.__bot_data_provider.get_avatar_url(),
                fields=[
                    EmbedField("Version", self.__environment.version.__str__()),
                    EmbedField("Latency", f"{self.__bot_data_provider.get_latency():,.2f} ms"),
                    EmbedField("Servers", str(self.__bot_data_provider.get_server_count())),
                    EmbedField("Server time", f"{current_time:%I:%M:%S %p, %m/%d/%Y %Z}"),
                    EmbedField("Repository", "https://github.com/rexor12/holobot")
                ],
                footer=EmbedFooter("Brought to you by rexor12", "https://avatars.githubusercontent.com/u/15330052")
            ))
        )
