from asyncio.exceptions import TimeoutError
from discord.embeds import Embed
from discord.ext.commands.context import Context
from discord.message import Message
from discord.reaction import Reaction
from holobot.bot import Bot
from holobot.logging.log_interface import LogInterface
from typing import Awaitable, Callable, Optional

import asyncio

DEFAULT_PAGE_SIZE: int = 5
DEFAULT_REACTION_PREVIOUS: str = "◀️"
DEFAULT_REACTION_NEXT: str = "▶️"

class DynamicPager(Awaitable[None]):
    def __init__(self, bot: Bot, context: Context, embed_factory: Callable[[Context, int, int], Awaitable[Optional[Embed]]]):
        self.current_page = 0
        self.reaction_next = DEFAULT_REACTION_NEXT
        self.reaction_previous = DEFAULT_REACTION_PREVIOUS
        self.__bot = bot
        self.__context = context
        self.__embed_factory = embed_factory
        self.__log = bot.service_collection.get(LogInterface)
    
    def __await__(self):
        yield from asyncio.get_event_loop().create_task(self.__run())
    
    @property
    def current_page(self) -> int:
        return self.__current_page
    
    @current_page.setter
    def current_page(self, value: int):
        self.__current_page = value
    
    @property
    def reaction_next(self) -> str:
        return self.__reaction_next
    
    @reaction_next.setter
    def reaction_next(self, value: str):
        self.__reaction_next = value
    
    @property
    def reaction_previous(self) -> str:
        return self.__reaction_previous
    
    @reaction_previous.setter
    def reaction_previous(self, value: str):
        self.__reaction_previous = value

    async def __run(self):
        context = self.__context
        if not (message := await self.__send_initial_page()):
            return
        self.__log.debug(f"[DynamicPager] Pager created. {{ UserId = {self.__context.author.id} }}")

        while True:
            try:
                reaction, user = await self.__bot.wait_for("reaction_add", timeout=60, check=self.__is_reaction_from_author)
                previous_page = self.current_page
                emoji = str(reaction.emoji)
                if emoji == self.reaction_next:
                    self.current_page += 1
                elif emoji == self.reaction_previous:
                    self.current_page -= 1
                else: continue

                await message.remove_reaction(reaction, user)
                if self.current_page < 0:
                    self.current_page = 0
                    continue

                if not (embed := await self.__embed_factory(context, self.current_page, DEFAULT_PAGE_SIZE)):
                    self.current_page = previous_page
                    continue

                await message.edit(embed=embed)
                self.__log.debug(f"[DynamicPager] Page changed. {{ UserId = {self.__context.author.id}, Page = {self.current_page} }}")
            except TimeoutError:
                await message.delete()
                break
        self.__log.debug(f"[DynamicPager] Pager destroyed. {{ UserId = {self.__context.author.id} }}")
    
    async def __send_initial_page(self) -> Optional[Message]:
        if not (embed := await self.__embed_factory(self.__context, self.current_page, DEFAULT_PAGE_SIZE)):
            await self.__context.reply("There's nothing to view.")
            return None
        
        message: Message = await self.__context.send(embed=embed)
        await message.add_reaction(self.reaction_previous)
        await message.add_reaction(self.reaction_next)

        return message

    def __is_reaction_from_author(self, reaction: Reaction, user) -> bool:
        return user == self.__context.author and str(reaction.emoji) in (self.reaction_previous, self.reaction_next)
