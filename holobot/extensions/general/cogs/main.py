from asyncio.tasks import sleep
from datetime import datetime
from discord.embeds import Embed
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import command, cooldown
from discord.ext.commands.errors import CommandOnCooldown, MissingRequiredArgument
from discord.message import Message
from discord.partial_emoji import PartialEmoji
from discord.user import User
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.bot import Bot
from holobot.discord.sdk.utils import find_emoji, find_member, reply
from holobot.sdk.logging import LogInterface
from holobot.sdk.system import EnvironmentInterface
from random import randint, randrange
from typing import Optional

import tzlocal

class General(Cog, name="General"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
        self.__log = bot.service_collection.get(LogInterface).with_name("General", "General")
        self.__environment = bot.service_collection.get(EnvironmentInterface)
    
    @cooldown(1, 10, BucketType.member)
    @command(aliases=["a"], brief="Displays the specified user's or the sender's avatar.")
    async def avatar(self, context: Context, *, name: Optional[str]):
        message: Optional[Message] = context.message
        if message is None:
            self.__log.warning(f"The message for the command '{context.command}' by user '{context.author.id}' is undefined.")
            await context.reply("An internal error has occurred. Please, try again a bit later.")
            return
        if len(message.mentions) > 1:
            await context.reply("You must mention a single user!")
            return

        user: Optional[User]
        if len(message.mentions) > 0:
            user = message.mentions[0]
        elif name is not None:
            user = find_member(context, name)
        else:
            user = message.author
        if user is None:
            await context.reply("The user you specified cannot be found. Please, try again after a moment.")
            return
        
        embed = Embed(
            title=f"{user.display_name}'s avatar",
            color=0xeb7d00
        ).set_image(url=user.avatar_url)
        await context.reply(embed=embed)
    
    @cog_ext.cog_slash(name="avatar", description="Displays a user's avatar.", options=[
        create_option("user", "The name or mention of the user. By default, it's yourself.", SlashCommandOptionType.STRING, False)
    ])
    async def slash_avatar(self, context: SlashContext, user: Optional[str] = None):
        member = context.author if user is None else find_member(context, user.strip())
        if not member:
            await reply(context, "The specified user cannot be found. Did you make a typo?")
            return
        
        embed = Embed(
            title=f"{member.display_name}'s avatar",
            color=0xeb7d00
        ).set_image(url=member.avatar_url)
        await reply(context, embed)
    
    @cooldown(1, 10, BucketType.member)
    @command(aliases=["e"], brief="Displays the specified emoji in a larger size.")
    async def emoji(self, context: Context, emoji: PartialEmoji):
        await context.reply(emoji.url)
    
    @cog_ext.cog_slash(name="emoji", description="Displays an emoji in a larger size.", options=[
        create_option("name", "The name of or the emoji itself.", SlashCommandOptionType.STRING, True)
    ])
    async def slash_emoji(self, context: SlashContext, name: str):
        if (emoji := await find_emoji(context, name)) is None:
            await reply(context, "The specified emoji cannot be found. Did you insert it properly?")
            return
        await reply(context, str(emoji.url))

    @cooldown(1, 10, BucketType.member)
    @command(brief="Rolls the dice.", description="Generates a random number between the specified lower and upper boundaries. If one boundary is specified only, it's considered as the upper boundary and the lower boundary defaults to 0.")
    async def roll(self, context: Context, boundary1: int, boundary2: int = None):
        if boundary2 is not None:
            if boundary2 <= boundary1:
                await context.send(f"{context.author.mention}, the second boundary must be greater than the first boundary!")
                self.roll.reset_cooldown(context)
                return
        else:
            if boundary1 <= 0:
                await context.send(f"{context.author.mention}, the specified number must be greater than 0!")
                self.roll.reset_cooldown(context)
                return
            boundary2 = boundary1
            boundary1 = 0
        temporary_message: Message = await context.send("Rolling the dice...")
        await sleep(3)
        await temporary_message.delete()
        await context.send(f"{context.author.mention}, you rolled {randrange(boundary1, boundary2)}.")

    @cog_ext.cog_slash(name="roll", description="Generates a random integer between the specified bounds.", options=[
        create_option("max", "The upper bound.", SlashCommandOptionType.INTEGER, True),
        create_option("min", "The lower bound. By default, it's 1.", SlashCommandOptionType.INTEGER, False)
    ])
    async def slash_roll(self, context: SlashContext, max: int, min: int = 1):
        if max < min:
            (min, max) = (max, min)
        await reply(context, f"You rolled {randint(min, max)}")

    @cog_ext.cog_slash(name="info", description="Displays some information about the bot.")
    async def slash_info(self, context: SlashContext):
        current_time = datetime.now(tzlocal.get_localzone())
        embed = Embed(
            title="Bot information", description="Basic information about the bot.", color=0xeb7d00
        ).set_thumbnail(
            url=self.__bot.user.avatar_url
        ).add_field(
            name="Version", value=f"{self.__environment.version}"
        ).add_field(
            name="Latency", value=f"{(self.__bot.latency * 1000):,.2f} ms"
        ).add_field(
            name="Servers", value=f"{len(self.__bot.guilds)}"
        ).add_field(
            name="Server time", value=f"{current_time:%I:%M:%S %p, %m/%d/%Y %Z}"
        ).add_field(
            name="Repository", value="https://github.com/rexor12/holobot"
        ).set_footer(text="Brought to you by rexor12")
        await reply(context, embed)

    @avatar.error
    @emoji.error
    @roll.error
    async def on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.send(f"{context.author.mention}, you're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        if isinstance(error, MissingRequiredArgument):
            await context.reply("You used an invalid syntax for this command. Please, see the help for more information.")
            return
        raise error

def setup(bot: Bot):
    bot.add_cog(General(bot))
