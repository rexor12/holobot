from .iconfig_provider import IConfigProvider
from .repositories import IWarnRepository
from asyncio.tasks import Task
from datetime import timedelta
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from typing import Awaitable, Optional

import asyncio

@injectable(StartableInterface)
class WarnCleanupProcessor(StartableInterface):
    def __init__(self,
        config_provider: IConfigProvider,
        log: LogInterface,
        warn_repository: IWarnRepository) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "WarnCleanupProcessor")
        self.__warn_repository: IWarnRepository = warn_repository
        self.__cleanup_interval: timedelta = config_provider.get_warn_cleanup_interval()
        self.__cleanup_delay: timedelta = config_provider.get_warn_cleanup_delay()
        self.__token_source: Optional[CancellationTokenSource] = None
        self.__background_task: Optional[Task[None]] = None
    
    async def start(self):
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__process_async(self.__token_source.token)
        )
        self.__log.info(f"Warn cleanup processor started. {{ Delay = {self.__cleanup_delay}, Interval = {self.__cleanup_interval} }}")
    
    async def stop(self):
        if self.__token_source: self.__token_source.cancel()
        if self.__background_task:
            try:
                await self.__background_task
            except asyncio.exceptions.CancelledError:
                pass
        self.__log.debug("Stopped background task.")

    async def __process_async(self, token: CancellationToken):
        await wait(int(self.__cleanup_delay.total_seconds()), token)
        interval = int(self.__cleanup_interval.total_seconds())
        while not token.is_cancellation_requested:
            self.__log.trace("Processing warn strikes...")
            cleared_warn_count = 0
            try:
                cleared_warn_count = await self.__warn_repository.clear_expired_warns()
            except Exception as error:
                self.__log.error(f"Processing failed. Further processing will stop. {{ Reason = UnexpectedError }}", error)
                raise
            finally:
                self.__log.trace(f"Processed warn strikes. {{ Count = {cleared_warn_count} }}")
            await wait(interval, token)
