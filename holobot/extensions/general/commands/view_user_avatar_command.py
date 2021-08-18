from discord.embeds import Embed
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import find_member, reply
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class ViewUserAvatarCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("avatar")
        self.description = "Displays a user's avatar."
        self.options = [
            create_option("user", "The name or mention of the user. By default, it's yourself.", SlashCommandOptionType.STRING, False)
        ]

    async def execute(self, context: SlashContext, user: Optional[str] = None) -> CommandResponse:
        member = context.author if user is None else find_member(context, user.strip())
        if not member:
            await reply(context, "The specified user cannot be found. Did you make a typo?")
            return CommandResponse()
        
        embed = Embed(
            title=f"{member.display_name}'s avatar",
            color=0xeb7d00
        ).set_image(url=member.avatar_url)
        await reply(context, embed)
        return CommandResponse()
