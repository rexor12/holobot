from .iconfig_provider import IConfigProvider
from .repositories import IWarnRepository
from asyncio.tasks import Task
from datetime import timedelta
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.threading import AsyncLoop
from typing import Optional

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
        self.__background_loop: Optional[AsyncLoop] = None
        self.__background_task: Optional[Task] = None
        self.__cleanup_interval: timedelta = config_provider.get_warn_cleanup_interval()
        self.__cleanup_delay: timedelta = config_provider.get_warn_cleanup_delay()
    
    async def start(self):
        self.__background_loop = AsyncLoop(
            self.__process_async,
            int(self.__cleanup_interval.total_seconds()),
            int(self.__cleanup_delay.total_seconds())
        )
        self.__background_task = asyncio.create_task(self.__background_loop())
        self.__log.info(f"Warn cleanup processor started. {{ Delay = {self.__cleanup_delay}, Interval = {self.__cleanup_interval} }}")
    
    async def stop(self):
        loop = self.__background_loop
        if loop: loop.cancel()
        task = self.__background_task
        if task: await task
        self.__log.debug("Stopped background task.")

    async def __process_async(self):
        self.__log.trace("Processing warn strikes...")
        cleared_warn_count = 0
        try:
            cleared_warn_count = await self.__warn_repository.clear_expired_warns()
        except Exception as error:
            self.__log.error(f"Processing failed. Further processing will stop. {{ Reason = UnexpectedError }}", error)
            raise
        finally:
            self.__log.trace(f"Processed warn strikes. {{ Count = {cleared_warn_count} }}")
