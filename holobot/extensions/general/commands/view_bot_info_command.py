from datetime import datetime
from discord.embeds import Embed
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import EnvironmentInterface

import tzlocal

@injectable(CommandInterface)
class ViewBotInfoCommand(CommandBase):
    def __init__(self, environment: EnvironmentInterface) -> None:
        super().__init__("info")
        self.__environment = environment
        self.description = "Displays some information about the bot."

    async def execute(self, context: SlashContext) -> None:
        current_time = datetime.now(tzlocal.get_localzone())
        embed = Embed(
            title="Bot information", description="Basic information about the bot.", color=0xeb7d00
        ).set_thumbnail(
            url=context.bot.user.avatar_url
        ).add_field(
            name="Version", value=f"{self.__environment.version}"
        ).add_field(
            name="Latency", value=f"{(context.bot.latency * 1000):,.2f} ms"
        ).add_field(
            name="Servers", value=f"{len(context.bot.guilds)}"
        ).add_field(
            name="Server time", value=f"{current_time:%I:%M:%S %p, %m/%d/%Y %Z}"
        ).add_field(
            name="Repository", value="https://github.com/rexor12/holobot"
        ).set_footer(text="Brought to you by rexor12")
        await reply(context, embed)
