from asyncio.tasks import sleep
from discord.enums import ActivityType
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import command, cooldown, has_permissions
from discord.ext.commands.errors import CommandOnCooldown
from discord.message import Message
from holobot.bot import Bot
from random import randrange

class General(Cog, name="General"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
    
    @cooldown(1, 10, BucketType.member)
    @command(brief="Repeats the specified text.")
    async def say(self, context: Context, *, message: str):
        await context.message.delete()
        await context.send(message)

    @cooldown(1, 10, BucketType.member)
    @command(brief="Rolls the dice. The second boundary is optional, used when you want to specify the range.")
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
        print(f"[Cog] [General] Changed status text to '{text}'.")

    @say.error
    @roll.error
    async def on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.send(f"{context.author.mention}, you're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        raise error

def setup(bot: Bot):
    bot.add_cog(General(bot))