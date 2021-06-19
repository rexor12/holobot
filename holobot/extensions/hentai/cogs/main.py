from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown, group
from discord.ext.commands.errors import CommandInvokeError, CommandOnCooldown, MissingRequiredArgument
from discord.message import DeletedReferencedMessage, Message, MessageReference
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.bot import Bot
from holobot.discord.sdk.utils import reply
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import try_parse_int
from typing import Optional

import re

NHENTAI_SITE_ID = "nhentai"
EHENTAI_SITE_ID = "ehentai"

ehentai_regex = re.compile(r"^(?:\d+)\/(?:[a-z0-9]{10})$")

class Hentai(Cog, name="Hentai"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot: Bot = bot
        self.__log: LogInterface = bot.service_collection.get(LogInterface)

    @group(aliases=["h"], brief="A group of hentai related commands.")
    async def hentai(self, context: Context):
        if not context.invoked_subcommand:
            await context.reply("You have to specify a sub-command!", delete_after=3)

    @cog_ext.cog_subcommand(base="hentai", name="link", description="Gives you a link to a title on a specific site.", options=[
        create_option("site", "The name of the site.", SlashCommandOptionType.STRING, True, choices=[
            create_choice(NHENTAI_SITE_ID, "nhentai"),
            create_choice(EHENTAI_SITE_ID, "e-hentai")
        ]),
        create_option("id", "The identifier of the title.", SlashCommandOptionType.STRING, True)
    ])
    async def slash_hentai(self, context: SlashContext, site: str, id: str):
        if not site or not id:
            await reply(context, "You must specify both the site and the identifier.")
            return
        id = id.strip()
        if site == NHENTAI_SITE_ID:
            if (value := try_parse_int(id)) is None:
                await reply(context, "Invalid identifier. A valid identifier, for example, is _206981_.")
                return
            await reply(context, f"https://nhentai.net/g/{value}")
        elif site == EHENTAI_SITE_ID:
            if not ehentai_regex.match(id):
                await reply(context, "Invalid identifier. A valid identifier, for example, is _1383239/0e7abac58a_ (case-sensitive).")
                return
            await reply(context, f"https://e-hentai.org/g/{id}")
        else: await reply(context, "You've specified an invalid site.")
    
    @cooldown(1, 10, BucketType.user)
    @hentai.command(aliases=["nh"], brief="Turns a number into an nhentai URL.")
    async def nhentai(self, context: Context, id: Optional[int]):
        if id is not None:
            await self.__reply_with_nhentai_url(context, id)
            return
        message: Message = context.message
        if message.reference is None or not isinstance(message.reference, MessageReference):
            await context.reply(f"Please, either specify an identifier or reply to a message with an identifier.")
            return
        resolved_message = message.reference.resolved
        if resolved_message is None:
            await context.reply(f"I couldn't figure out the code from the referenced message. This may be caused by a Discord error. Please, type the identifier manually.")
            return
        if isinstance(resolved_message, DeletedReferencedMessage):
            await context.reply("The referenced message has been deleted. Please, type the identifier manually.")
            return
        if isinstance(resolved_message, Message):
            if (value := try_parse_int(resolved_message.content)) is None:
                await context.reply(f"The referenced message is something that isn't a proper identifier.")
                return
            await self.__reply_with_nhentai_url(context, value)
            return
        await context.reply("I don't understand the referenced message. This may be a new Discord feature I'm not familiar with. Please, type the identifier manually.")
    
    async def __reply_with_nhentai_url(self, context: Context, id: int) -> None:
        await context.reply(f"https://nhentai.net/g/{id}")

    @nhentai.error
    async def __on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.reply(f"You're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        if isinstance(error, MissingRequiredArgument):
            await context.reply("You used an invalid syntax for this command. Please, see the help for more information.")
            return
        if isinstance(error, CommandInvokeError) and isinstance(error.original, TimeoutError):
            return
        await context.reply("An internal error has occurred. Please, try again later.")
        self.__log.error(f"[Cogs] [Hentai] Failed to process the command '{context.command}'.", error)
    
def setup(bot: Bot):
    bot.add_cog(Hentai(bot))
