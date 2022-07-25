from .iconfig_provider import IConfigProvider
from .managers import ILogManager, IMuteManager
from .repositories import IMutesRepository
from asyncio.tasks import Task
from datetime import timedelta
from holobot.discord.sdk.exceptions import ForbiddenError, ServerNotFoundError, UserNotFoundError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from typing import Awaitable, Optional

import asyncio

@injectable(StartableInterface)
class MuteCleanupProcessor(StartableInterface):
    def __init__(self,
        config_provider: IConfigProvider,
        log_manager: ILogManager,
        logger_factory: ILoggerFactory,
        mute_manager: IMuteManager,
        mutes_repository: IMutesRepository) -> None:
        super().__init__()
        self.__logger = logger_factory.create(MuteCleanupProcessor)
        self.__log_manager: ILogManager = log_manager
        self.__mute_manager: IMuteManager = mute_manager
        self.__mutes_repository: IMutesRepository = mutes_repository
        self.__cleanup_interval: timedelta = config_provider.get_mute_cleanup_interval()
        self.__cleanup_delay: timedelta = config_provider.get_mute_cleanup_delay()
        self.__token_source: Optional[CancellationTokenSource] = None
        self.__background_task: Optional[Awaitable[None]] = None
    
    async def start(self):
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__process_async(self.__token_source.token)
        )
        self.__logger.info(f"Mute cleanup processor started. {{ Delay = {self.__cleanup_delay}, Interval = {self.__cleanup_interval} }}")
    
    async def stop(self):
        if self.__token_source: self.__token_source.cancel()
        if self.__background_task:
            try:
                await self.__background_task
            except asyncio.exceptions.CancelledError:
                pass
        self.__logger.debug("Stopped background task.")

    async def __process_async(self, token: CancellationToken):
        await wait(int(self.__cleanup_delay.total_seconds()), token)
        interval = int(self.__cleanup_interval.total_seconds())
        while not token.is_cancellation_requested:
            self.__logger.trace("Processing mutes...")
            cleared_mute_count = 0
            try:
                mutes = await self.__mutes_repository.delete_expired_mutes()
                for mute in mutes:
                    await self.__try_unmute_user(mute.server_id, mute.user_id)
                    cleared_mute_count = cleared_mute_count + 1
            except Exception as error:
                self.__logger.error(f"Processing failed. Further processing will stop. {{ Reason = UnexpectedError }}", error)
                raise
            finally:
                self.__logger.trace(f"Processed mutes. {{ Count = {cleared_mute_count} }}")
            await wait(interval, token)
    
    async def __try_unmute_user(self, server_id: str, user_id: str) -> None:
        try:
            await self.__mute_manager.unmute_user(server_id, user_id, False)
            await self.__log_manager.publish_log_entry(server_id, f":loud_sound: <@{user_id}> has been unmuted automatically as their punishment has expired.")
        except (ForbiddenError, ServerNotFoundError, UserNotFoundError):
            pass
