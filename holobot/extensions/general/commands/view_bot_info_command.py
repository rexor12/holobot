from datetime import datetime
from holobot.discord.sdk import IBotDataProvider
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import EnvironmentInterface

import tzlocal

@injectable(CommandInterface)
class ViewBotInfoCommand(CommandBase):
    def __init__(self, bot_data_provider: IBotDataProvider, environment: EnvironmentInterface) -> None:
        super().__init__("info")
        self.__bot_data_provider: IBotDataProvider = bot_data_provider
        self.__environment = environment
        self.description = "Displays some information about the bot."

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        current_time = datetime.now(tzlocal.get_localzone())
        return CommandResponse(
            action=ReplyAction(Embed(
                title="Bot information",
                description="Basic information about the bot.",
                thumbnail_url=self.__bot_data_provider.get_thumbnail_url(),
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
