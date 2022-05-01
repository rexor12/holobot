from .. import IMessaging
from ..models import Embed, Reaction
from asyncio.exceptions import TimeoutError
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import MessageNotFoundError
from holobot.discord.sdk.models import InteractionContext, Message, Reaction
from holobot.sdk.logging import LogInterface
from typing import Any, Awaitable, Callable, Generator, Generic, Optional, TypeVar

import asyncio

DEFAULT_PAGE_SIZE: int = 5
DEFAULT_REACTION_PREVIOUS: str = "◀️"
DEFAULT_REACTION_NEXT: str = "▶️"

TContext = TypeVar("TContext", bound=InteractionContext)

class Pager(Generic[TContext], Awaitable[Any]):
    def __init__(self,
        messaging: IMessaging,
        log: LogInterface,
        context: TContext,
        embed_factory: Callable[[TContext, int, int], Awaitable[Optional[Embed]]],
        initial_page: int = 0):
        self.current_page = initial_page
        self.reaction_next = DEFAULT_REACTION_NEXT
        self.reaction_previous = DEFAULT_REACTION_PREVIOUS
        self.__messaging = messaging
        self.__log = log
        self.__context = context
        self.__embed_factory = embed_factory
    
    def __await__(self) -> Generator[Any, None, None]:
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

    async def __run(self) -> None:
        if not (message := await self.__send_initial_page(self.__context)):
            return
        self.__log.trace(f"Pager created. {{ UserId = {self.__context.author_id} }}")

        while True:
            try:
                message_id = message.message_id
                reaction = await self.__messaging.wait_for_reaction(lambda r: self.__is_reaction_from_author(r, message_id))
                self.__log.trace(f"Reaction added. {{ OwnerId = {reaction.owner_id}, MessageId = {message_id} }}")
                if not reaction.owner_id:
                    self.__log.debug(f"Received a reaction without an owner. {{ EmojiId = {reaction.emoji_id} }}")
                    continue
                
                previous_page = self.current_page
                if reaction.emoji_id == self.reaction_next:
                    self.current_page += 1
                elif reaction.emoji_id == self.reaction_previous:
                    self.current_page -= 1
                else: continue

                await self.__messaging.remove_reaction(self.__context, message, reaction.owner_id, reaction.emoji_id)
                if self.current_page < 0:
                    self.current_page = 0
                    continue

                if not (embed := await self.__embed_factory(self.__context, self.current_page, DEFAULT_PAGE_SIZE)):
                    self.current_page = previous_page
                    continue

                await self.__messaging.edit_message(self.__context, message, embed)
                self.__log.trace(f"Page changed. {{ UserId = {self.__context.author_id}, Page = {self.current_page} }}")
            except TimeoutError:
                await self.__delete_message(message)
                break
            except MessageNotFoundError:
                self.__log.trace(f"Tried to edit non-existent message. {{ MessageId = {message} }}")
            except Exception as error:
                self.__log.warning(f"Unexpected exception. {{ Type = {type(error)}, Message = {error} }}")
                raise
        self.__log.trace(f"Pager destroyed. {{ UserId = {self.__context.author_id} }}")
    
    async def __send_initial_page(self, context: TContext) -> Optional[Message]:
        if not (embed := await self.__embed_factory(self.__context, self.current_page, DEFAULT_PAGE_SIZE)):
            await self.__messaging.send_context_reply(context, "There's nothing to view.")
            return None

        reply_id = await self.__messaging.send_context_reply(context, embed)
        await self.__messaging.add_reaction(self.__context, reply_id, self.reaction_previous)
        await self.__messaging.add_reaction(self.__context, reply_id, self.reaction_next)

        return reply_id

    def __is_reaction_from_author(self, reaction: Reaction, message_id: str) -> bool:
        return (reaction.owner_id == self.__context.author_id
                and reaction.message_id == message_id
                and reaction.emoji_id in (self.reaction_previous, self.reaction_next))
    
    async def __delete_message(self, message: Message) -> None:
        try:
            await self.__messaging.delete_message(self.__context, message)
        except MessageNotFoundError:
                self.__log.trace(f"Tried to delete a non-existent message. {{ MessageId = {message.message_id} }}")
        except Exception as error:
            self.__log.warning(f"Failed to delete a message. {{ Type = {type(error)}, Message = {error} }}")
