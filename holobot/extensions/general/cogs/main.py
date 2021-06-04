from asyncio.tasks import sleep
from datetime import datetime
from discord.embeds import Embed
from discord.enums import ActivityType
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import command, cooldown, has_permissions
from discord.ext.commands.errors import CommandOnCooldown, MissingRequiredArgument
from discord.message import Message
from discord.partial_emoji import PartialEmoji
from discord.user import User
from holobot.discord.bot import Bot
from holobot.discord.sdk.utils import find_member
from holobot.sdk.logging import LogInterface
from holobot.sdk.system import EnvironmentInterface
from random import randrange
from typing import Optional

import tzlocal

class General(Cog, name="General"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
        self.__log = bot.service_collection.get(LogInterface)
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
    
    @cooldown(1, 10, BucketType.member)
    @command(aliases=["e"], brief="Displays the specified emoji in a larger size.")
    async def emoji(self, context: Context, emoji: PartialEmoji):
        await context.reply(emoji.url)
    
    @cooldown(1, 10, BucketType.member)
    @command(brief="Repeats the specified text.")
    async def say(self, context: Context, *, message: str):
        await context.message.delete()
        await context.send(message)

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
    
    @command(aliases=["status"], hidden=True)
    @has_permissions(administrator=True)
    async def set_status_text(self, context: Context, *, text: str):
        await self.__bot.set_status_text(ActivityType.watching, text)
        self.__log.info(f"[Cog] [General] Changed status text to '{text}'.")
    
    @cooldown(1, 10, BucketType.member)
    @command(brief="Tells the current version of the bot.")
    async def version(self, context: Context):
        await context.send(f"{context.author.mention}, my current version is {self.__environment.version}.")
    
    @cooldown(1, 60, BucketType.user)
    @command(brief="Displays the bot's current date and time.", description="Displays the current date and time at the server hosting the bot.")
    async def servertime(self, context: Context):
        current_time = datetime.now(tzlocal.get_localzone())
        await context.reply(f"The current date and time is {current_time:%I:%M:%S %p, %m/%d/%Y %Z}.")

    @avatar.error
    @emoji.error
    @say.error
    @roll.error
    @version.error
    @servertime.error
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
