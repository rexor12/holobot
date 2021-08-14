from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import find_emoji, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ViewEmojiCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("emoji")
        self.description = "Displays an emoji in a larger size."
        self.options = [
            create_option("name", "The name of or the emoji itself.", SlashCommandOptionType.STRING, True)
        ]

    async def execute(self, context: SlashContext, name: str) -> CommandResponse:
        if (emoji := await find_emoji(context, name)) is None:
            await reply(context, "The specified emoji cannot be found. Did you make a typo?")
            return CommandResponse()
        await reply(context, str(emoji.url))
        return CommandResponse()
