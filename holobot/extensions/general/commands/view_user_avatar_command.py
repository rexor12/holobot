from discord.embeds import Embed
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class ViewUserAvatarCommand(CommandBase):
    def __init__(self, member_data_provider: IMemberDataProvider) -> None:
        super().__init__("avatar")
        self.description = "Displays a user's avatar."
        self.options = [
            create_option("user", "The name or mention of the user. By default, it's yourself.", SlashCommandOptionType.STRING, False)
        ]
        self.__member_data_provider: IMemberDataProvider = member_data_provider

    async def execute(self, context: SlashContext, user: Optional[str] = None) -> CommandResponse:
        try:
            if user is None:
                member = self.__member_data_provider.get_basic_data_by_id(str(context.guild_id), str(context.author_id))
            elif (user_id := get_user_id(user)) is not None:
                member = self.__member_data_provider.get_basic_data_by_id(str(context.guild_id), user_id)
            else:
                member = self.__member_data_provider.get_basic_data_by_name(str(context.guild_id), user.strip())
        except:
            # TODO guild/user not found
            await reply(context, "The specified user cannot be found. Did you make a typo?")
            return CommandResponse()
        
        embed = Embed(
            title=f"{member.display_name}'s avatar",
            color=0xeb7d00
        ).set_image(url=member.avatar_url)
        await reply(context, embed)
        return CommandResponse()
