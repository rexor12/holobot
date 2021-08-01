from asyncio.exceptions import TimeoutError
from discord.embeds import Embed
from discord.errors import NotFound
from discord.ext.commands.context import Context
from discord.message import Message
from discord_slash.context import SlashContext
from discord_slash.model import SlashMessage
from holobot.discord.sdk.utils import find_member_by_id, get_author_id, reply
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.integration.models import Reaction
from holobot.sdk.logging import LogInterface
from typing import Awaitable, Callable, Optional, Union

import asyncio

DEFAULT_PAGE_SIZE: int = 5
DEFAULT_REACTION_PREVIOUS: str = "◀️"
DEFAULT_REACTION_NEXT: str = "▶️"

# TODO The dynamic pager component should be in the SDK for extensions.
class DynamicPager(Awaitable[None]):
    def __init__(self,
        messaging: MessagingInterface,
        log: LogInterface,
        context: Union[Context, SlashContext],
        embed_factory: Callable[[Union[Context, SlashContext], int, int], Awaitable[Optional[Embed]]]):
        self.current_page = 0
        self.reaction_next = DEFAULT_REACTION_NEXT
        self.reaction_previous = DEFAULT_REACTION_PREVIOUS
        self.__messaging = messaging
        self.__log = log
        self.__context = context
        self.__embed_factory = embed_factory
    
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
        self.__log.trace(f"Pager created. {{ UserId = {get_author_id(self.__context)} }}")

        while True:
            try:
                reaction = await self.__messaging.wait_for_reaction(lambda r: self.__is_reaction_from_author(r, message))
                self.__log.trace(f"Reaction added. {{ OwnerId = {reaction.owner_id}, MessageId = {message.id} }}")
                if not reaction.owner_id:
                    self.__log.debug(f"Received a reaction without an owner. {{ EmojiId = {reaction.emoji_id} }}")
                    continue
                
                previous_page = self.current_page
                if reaction.emoji_id == self.reaction_next:
                    self.current_page += 1
                elif reaction.emoji_id == self.reaction_previous:
                    self.current_page -= 1
                else: continue

                await message.remove_reaction(reaction.emoji_id, find_member_by_id(self.__context, reaction.owner_id))
                if self.current_page < 0:
                    self.current_page = 0
                    continue

                if not (embed := await self.__embed_factory(context, self.current_page, DEFAULT_PAGE_SIZE)):
                    self.current_page = previous_page
                    continue

                await message.edit(embed=embed)
                self.__log.trace(f"Page changed. {{ UserId = {self.__context.author.id}, Page = {self.current_page} }}")
            except TimeoutError:
                await message.delete()
                break
            except NotFound: # The message was probably deleted by someone.
                pass
        self.__log.trace(f"Pager destroyed. {{ UserId = {self.__context.author.id} }}")
    
    async def __send_initial_page(self) -> Optional[Union[Message, SlashMessage]]:
        if not (embed := await self.__embed_factory(self.__context, self.current_page, DEFAULT_PAGE_SIZE)):
            await reply(self.__context, "There's nothing to view.")
            return None
        
        message = await reply(self.__context, embed)
        await message.add_reaction(self.reaction_previous)
        await message.add_reaction(self.reaction_next)

        return message

    def __is_reaction_from_author(self, reaction: Reaction, message: Union[Message, SlashMessage]) -> bool:
        return (reaction.owner_id == get_author_id(self.__context)
                and reaction.message_id == str(message.id)
                and reaction.emoji_id in (self.reaction_previous, self.reaction_next))
